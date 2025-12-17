"""Tests for OAuth authentication endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.models.user import User
from app.services.auth import auth_service
from app.services.oauth import OAuthUserInfo


def get_error_message(response_data: dict) -> str:
    """Extract error message from response data (handles different formats)."""
    return (
        response_data.get("detail")
        or response_data.get("message")
        or str(response_data)
    ).lower()


class TestOAuthProviders:
    """Tests for OAuth providers endpoint."""

    @pytest.mark.asyncio
    async def test_get_oauth_providers(self, client: AsyncClient):
        """Test getting available OAuth providers."""
        response = await client.get("/api/auth/oauth/providers")

        assert response.status_code == 200
        data = response.json()
        assert "google" in data
        assert "github" in data
        # By default, OAuth is not configured in tests
        assert data["google"] is False
        assert data["github"] is False


class TestGoogleOAuth:
    """Tests for Google OAuth endpoints."""

    @pytest.mark.asyncio
    async def test_google_auth_url_not_configured(self, client: AsyncClient):
        """Test Google auth URL when not configured."""
        response = await client.get("/api/auth/oauth/google")
        assert response.status_code == 501
        assert "not configured" in get_error_message(response.json())

    @pytest.mark.asyncio
    async def test_google_callback_not_configured(self, client: AsyncClient):
        """Test Google callback when not configured."""
        response = await client.post("/api/auth/oauth/google/callback", json={
            "code": "test_code",
            "state": "test_state",
        })
        assert response.status_code == 501

    @pytest.mark.asyncio
    async def test_google_auth_url_configured(self, client: AsyncClient):
        """Test Google auth URL when configured."""
        with patch("app.services.oauth.settings") as mock_settings:
            mock_settings.google_client_id = "test_client_id"
            mock_settings.google_client_secret = "test_secret"
            mock_settings.oauth_redirect_url = "http://localhost:5173/auth/callback"

            with patch("app.api.auth.oauth_service.is_google_configured", return_value=True):
                with patch("app.api.auth.oauth_service.get_google_auth_url") as mock_get_url:
                    mock_get_url.return_value = ("https://accounts.google.com/oauth?...", "test_state")

                    response = await client.get("/api/auth/oauth/google")

                    assert response.status_code == 200
                    data = response.json()
                    assert "authorization_url" in data
                    assert "state" in data

    @pytest.mark.asyncio
    async def test_google_callback_invalid_state(self, client: AsyncClient):
        """Test Google callback with invalid state."""
        with patch("app.api.auth.oauth_service.is_google_configured", return_value=True):
            with patch("app.api.auth.oauth_service.validate_state", return_value=False):
                response = await client.post("/api/auth/oauth/google/callback", json={
                    "code": "test_code",
                    "state": "invalid_state",
                })

                assert response.status_code == 400
                assert "state" in get_error_message(response.json())

    @pytest.mark.asyncio
    async def test_google_callback_success_new_user(self, client: AsyncClient, init_test_db):
        """Test successful Google OAuth callback creating new user."""
        mock_user_info = OAuthUserInfo(
            email="google_user@example.com",
            provider_id="google_123",
            provider="google",
            full_name="Google User",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
        )

        with patch("app.api.auth.oauth_service.is_google_configured", return_value=True):
            with patch("app.api.auth.oauth_service.validate_state", return_value=True):
                with patch("app.api.auth.oauth_service.exchange_google_code", new_callable=AsyncMock) as mock_exchange:
                    mock_exchange.return_value = mock_user_info

                    response = await client.post("/api/auth/oauth/google/callback", json={
                        "code": "valid_code",
                        "state": "valid_state",
                    })

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert "refresh_token" in data

                    # Verify user was created
                    user = await User.find_one(User.email == "google_user@example.com")
                    assert user is not None
                    assert user.google_id == "google_123"
                    assert user.email_verified is True


class TestGitHubOAuth:
    """Tests for GitHub OAuth endpoints."""

    @pytest.mark.asyncio
    async def test_github_auth_url_not_configured(self, client: AsyncClient):
        """Test GitHub auth URL when not configured."""
        response = await client.get("/api/auth/oauth/github")
        assert response.status_code == 501
        assert "not configured" in get_error_message(response.json())

    @pytest.mark.asyncio
    async def test_github_callback_not_configured(self, client: AsyncClient):
        """Test GitHub callback when not configured."""
        response = await client.post("/api/auth/oauth/github/callback", json={
            "code": "test_code",
            "state": "test_state",
        })
        assert response.status_code == 501

    @pytest.mark.asyncio
    async def test_github_callback_success_new_user(self, client: AsyncClient, init_test_db):
        """Test successful GitHub OAuth callback creating new user."""
        mock_user_info = OAuthUserInfo(
            email="github_user@example.com",
            provider_id="github_456",
            provider="github",
            full_name="GitHub User",
            avatar_url="https://github.com/avatar.jpg",
            email_verified=True,
        )

        with patch("app.api.auth.oauth_service.is_github_configured", return_value=True):
            with patch("app.api.auth.oauth_service.validate_state", return_value=True):
                with patch("app.api.auth.oauth_service.exchange_github_code", new_callable=AsyncMock) as mock_exchange:
                    mock_exchange.return_value = mock_user_info

                    response = await client.post("/api/auth/oauth/github/callback", json={
                        "code": "valid_code",
                        "state": "valid_state",
                    })

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert "refresh_token" in data

                    # Verify user was created
                    user = await User.find_one(User.email == "github_user@example.com")
                    assert user is not None
                    assert user.github_id == "github_456"


class TestOAuthLinkUnlink:
    """Tests for OAuth account linking/unlinking."""

    @pytest.fixture
    async def user_with_password(self, init_test_db):
        """Create a user with password for testing."""
        user = await auth_service.create_user(
            email="linktest@example.com",
            password="TestPass123",
            full_name="Link Test User",
        )
        return user

    @pytest.fixture
    async def auth_headers_for_user(self, user_with_password):
        """Get auth headers for the test user."""
        tokens = auth_service.create_token_pair(user_with_password)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    @pytest.mark.asyncio
    async def test_unlink_google_no_account_linked(
        self, client: AsyncClient, user_with_password, auth_headers_for_user
    ):
        """Test unlinking Google when no account is linked."""
        response = await client.delete(
            "/api/auth/oauth/google/unlink",
            headers=auth_headers_for_user,
        )

        assert response.status_code == 400
        assert "no google account linked" in get_error_message(response.json())

    @pytest.mark.asyncio
    async def test_unlink_github_no_account_linked(
        self, client: AsyncClient, user_with_password, auth_headers_for_user
    ):
        """Test unlinking GitHub when no account is linked."""
        response = await client.delete(
            "/api/auth/oauth/github/unlink",
            headers=auth_headers_for_user,
        )

        assert response.status_code == 400
        assert "no github account linked" in get_error_message(response.json())

    @pytest.mark.asyncio
    async def test_unlink_google_success(
        self, client: AsyncClient, init_test_db, auth_headers_for_user
    ):
        """Test successfully unlinking Google account."""
        # First, create a user with Google linked
        user = await auth_service.create_user(
            email="unlink_google@example.com",
            password="TestPass123",
            google_id="google_to_unlink",
        )
        tokens = auth_service.create_token_pair(user)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = await client.delete(
            "/api/auth/oauth/google/unlink",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["google_connected"] is False

        # Verify in database
        updated_user = await User.get(user.id)
        assert updated_user.google_id is None

    @pytest.mark.asyncio
    async def test_unlink_github_success(
        self, client: AsyncClient, init_test_db
    ):
        """Test successfully unlinking GitHub account."""
        # First, create a user with GitHub linked
        user = await auth_service.create_user(
            email="unlink_github@example.com",
            password="TestPass123",
            github_id="github_to_unlink",
        )
        tokens = auth_service.create_token_pair(user)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = await client.delete(
            "/api/auth/oauth/github/unlink",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["github_connected"] is False

        # Verify in database
        updated_user = await User.get(user.id)
        assert updated_user.github_id is None

    @pytest.mark.asyncio
    async def test_unlink_prevents_lockout(
        self, client: AsyncClient, init_test_db
    ):
        """Test that unlinking is prevented if it would lock user out."""
        # Create OAuth-only user
        user = await auth_service.create_user(
            email="oauth_only@example.com",
            google_id="google_only",
        )
        tokens = auth_service.create_token_pair(user)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        response = await client.delete(
            "/api/auth/oauth/google/unlink",
            headers=headers,
        )

        assert response.status_code == 400
        assert "no other authentication method" in get_error_message(response.json())


class TestOAuthAccountLinking:
    """Tests for OAuth account linking to existing users."""

    @pytest.mark.asyncio
    async def test_oauth_links_to_existing_email(self, client: AsyncClient, init_test_db):
        """Test that OAuth login links to existing user with same email."""
        # Create existing user with password
        existing_user = await auth_service.create_user(
            email="existing@example.com",
            password="TestPass123",
        )

        mock_user_info = OAuthUserInfo(
            email="existing@example.com",  # Same email
            provider_id="google_new",
            provider="google",
            full_name="Google Name",
            email_verified=True,
        )

        with patch("app.api.auth.oauth_service.is_google_configured", return_value=True):
            with patch("app.api.auth.oauth_service.validate_state", return_value=True):
                with patch("app.api.auth.oauth_service.exchange_google_code", new_callable=AsyncMock) as mock_exchange:
                    mock_exchange.return_value = mock_user_info

                    response = await client.post("/api/auth/oauth/google/callback", json={
                        "code": "valid_code",
                        "state": "valid_state",
                    })

                    assert response.status_code == 200

                    # Verify the existing user was updated, not a new one created
                    users = await User.find(User.email == "existing@example.com").to_list()
                    assert len(users) == 1
                    assert users[0].id == existing_user.id
                    assert users[0].google_id == "google_new"
