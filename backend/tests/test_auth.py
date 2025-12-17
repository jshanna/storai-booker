"""Tests for authentication API endpoints."""
import pytest
from httpx import AsyncClient

from app.models.user import User
from app.services.auth import auth_service


@pytest.fixture
async def registered_user(init_test_db):
    """Create a registered user for testing."""
    user = await auth_service.create_user(
        email="test@example.com",
        password="TestPass123",
        full_name="Test User",
    )
    return user


@pytest.fixture
async def auth_tokens(registered_user):
    """Get auth tokens for the registered user."""
    return auth_service.create_token_pair(registered_user)


class TestAuthService:
    """Tests for the authentication service."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "SecurePass123"
        hashed = auth_service.hash_password(password)

        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("WrongPass", hashed)

    def test_create_access_token(self):
        """Test access token creation."""
        token, expires = auth_service.create_access_token("user123", "test@example.com")

        assert token is not None
        assert len(token) > 0

        # Validate token
        payload = auth_service.validate_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        token, expires = auth_service.create_refresh_token("user123")

        assert token is not None

        # Validate token
        payload = auth_service.validate_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"
        assert "jti" in payload

    def test_invalid_token_validation(self):
        """Test that invalid tokens are rejected."""
        assert auth_service.validate_access_token("invalid_token") is None
        assert auth_service.validate_refresh_token("invalid_token") is None

    def test_token_type_mismatch(self):
        """Test that tokens are only valid for their type."""
        access_token, _ = auth_service.create_access_token("user123", "test@example.com")
        refresh_token, _ = auth_service.create_refresh_token("user123")

        # Access token should not validate as refresh
        assert auth_service.validate_refresh_token(access_token) is None
        # Refresh token should not validate as access
        assert auth_service.validate_access_token(refresh_token) is None


class TestRegisterEndpoint:
    """Tests for the /api/auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User",
        })

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, registered_user):
        """Test registration with duplicate email."""
        response = await client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "AnotherPass123",
        })

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "weak",  # Too short, no uppercase, no digit
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass123",
        })

        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for the /api/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, registered_user):
        """Test successful login."""
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        """Test login with wrong password."""
        response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass123",
        })

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email."""
        response = await client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePass123",
        })

        assert response.status_code == 401


class TestMeEndpoint:
    """Tests for the /api/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, registered_user, auth_tokens):
        """Test getting current user profile."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client: AsyncClient):
        """Test getting profile without token."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting profile with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestRefreshTokenEndpoint:
    """Tests for the /api/auth/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, auth_tokens):
        """Test successful token refresh."""
        response = await client.post("/api/auth/refresh", json={
            "refresh_token": auth_tokens["refresh_token"],
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_refresh_token",
        })

        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Tests for the /api/auth/change-password endpoint."""

    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, registered_user, auth_tokens):
        """Test successful password change."""
        response = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "TestPass123",
                "new_password": "NewSecure456",
            },
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        assert response.status_code == 200

        # Verify new password works
        login_response = await client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "NewSecure456",
        })
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client: AsyncClient, registered_user, auth_tokens):
        """Test password change with wrong current password."""
        response = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "WrongCurrent123",
                "new_password": "NewSecure456",
            },
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )

        assert response.status_code == 400
