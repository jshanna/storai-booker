"""OAuth service for Google and GitHub authentication."""
from typing import Optional, Tuple
from dataclasses import dataclass
import secrets

from authlib.integrations.httpx_client import AsyncOAuth2Client
from loguru import logger

from app.core.config import settings


@dataclass
class OAuthUserInfo:
    """User information from OAuth provider."""

    email: str
    provider_id: str
    provider: str  # "google" or "github"
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email_verified: bool = False


class OAuthService:
    """Service for OAuth authentication with Google and GitHub."""

    # OAuth provider configurations
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_SCOPES = ["openid", "email", "profile"]

    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USERINFO_URL = "https://api.github.com/user"
    GITHUB_EMAILS_URL = "https://api.github.com/user/emails"
    GITHUB_SCOPES = ["read:user", "user:email"]

    def __init__(self):
        """Initialize OAuth service."""
        self._state_store: dict[str, str] = {}  # In production, use Redis

    def _get_google_client(self, redirect_uri: str) -> AsyncOAuth2Client:
        """Create Google OAuth client."""
        return AsyncOAuth2Client(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            redirect_uri=redirect_uri,
            scope=" ".join(self.GOOGLE_SCOPES),
        )

    def _get_github_client(self, redirect_uri: str) -> AsyncOAuth2Client:
        """Create GitHub OAuth client."""
        return AsyncOAuth2Client(
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            redirect_uri=redirect_uri,
            scope=" ".join(self.GITHUB_SCOPES),
        )

    def is_google_configured(self) -> bool:
        """Check if Google OAuth is configured."""
        return bool(settings.google_client_id and settings.google_client_secret)

    def is_github_configured(self) -> bool:
        """Check if GitHub OAuth is configured."""
        return bool(settings.github_client_id and settings.github_client_secret)

    def generate_state(self) -> str:
        """Generate a secure state parameter for OAuth."""
        state = secrets.token_urlsafe(32)
        self._state_store[state] = state
        return state

    def validate_state(self, state: str) -> bool:
        """Validate and consume state parameter."""
        if state in self._state_store:
            del self._state_store[state]
            return True
        return False

    # Google OAuth Methods

    def get_google_auth_url(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Get Google OAuth authorization URL.

        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.is_google_configured():
            raise ValueError("Google OAuth is not configured")

        state = self.generate_state()
        client = self._get_google_client(redirect_uri)

        auth_url, _ = client.create_authorization_url(
            self.GOOGLE_AUTH_URL,
            state=state,
            access_type="offline",
            prompt="consent",
        )

        return auth_url, state

    async def exchange_google_code(
        self, code: str, redirect_uri: str
    ) -> OAuthUserInfo:
        """
        Exchange Google authorization code for user info.

        Args:
            code: Authorization code from Google callback
            redirect_uri: The redirect URI used in the initial request

        Returns:
            OAuthUserInfo with user details
        """
        if not self.is_google_configured():
            raise ValueError("Google OAuth is not configured")

        client = self._get_google_client(redirect_uri)

        try:
            # Exchange code for token
            token = await client.fetch_token(
                self.GOOGLE_TOKEN_URL,
                code=code,
            )

            # Fetch user info
            client.token = token
            resp = await client.get(self.GOOGLE_USERINFO_URL)
            resp.raise_for_status()
            user_data = resp.json()

            logger.debug(f"Google user data: {user_data}")

            return OAuthUserInfo(
                email=user_data["email"],
                provider_id=user_data["id"],
                provider="google",
                full_name=user_data.get("name"),
                avatar_url=user_data.get("picture"),
                email_verified=user_data.get("verified_email", False),
            )
        except Exception as e:
            logger.error(f"Failed to exchange Google code: {e}")
            raise
        finally:
            await client.aclose()

    # GitHub OAuth Methods

    def get_github_auth_url(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Get GitHub OAuth authorization URL.

        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.is_github_configured():
            raise ValueError("GitHub OAuth is not configured")

        state = self.generate_state()
        client = self._get_github_client(redirect_uri)

        auth_url, _ = client.create_authorization_url(
            self.GITHUB_AUTH_URL,
            state=state,
        )

        return auth_url, state

    async def exchange_github_code(
        self, code: str, redirect_uri: str
    ) -> OAuthUserInfo:
        """
        Exchange GitHub authorization code for user info.

        Args:
            code: Authorization code from GitHub callback
            redirect_uri: The redirect URI used in the initial request

        Returns:
            OAuthUserInfo with user details
        """
        if not self.is_github_configured():
            raise ValueError("GitHub OAuth is not configured")

        client = self._get_github_client(redirect_uri)

        try:
            # Exchange code for token
            token = await client.fetch_token(
                self.GITHUB_TOKEN_URL,
                code=code,
                headers={"Accept": "application/json"},
            )

            # Fetch user info
            client.token = token
            resp = await client.get(
                self.GITHUB_USERINFO_URL,
                headers={"Accept": "application/vnd.github+json"},
            )
            resp.raise_for_status()
            user_data = resp.json()

            logger.debug(f"GitHub user data: {user_data}")

            # Get email (may need separate request if not public)
            email = user_data.get("email")
            email_verified = False

            if not email:
                # Fetch emails from separate endpoint
                emails_resp = await client.get(
                    self.GITHUB_EMAILS_URL,
                    headers={"Accept": "application/vnd.github+json"},
                )
                emails_resp.raise_for_status()
                emails_data = emails_resp.json()

                # Find primary email
                for email_entry in emails_data:
                    if email_entry.get("primary"):
                        email = email_entry["email"]
                        email_verified = email_entry.get("verified", False)
                        break

                # Fallback to first verified email
                if not email:
                    for email_entry in emails_data:
                        if email_entry.get("verified"):
                            email = email_entry["email"]
                            email_verified = True
                            break

            if not email:
                raise ValueError("Could not retrieve email from GitHub")

            return OAuthUserInfo(
                email=email,
                provider_id=str(user_data["id"]),
                provider="github",
                full_name=user_data.get("name"),
                avatar_url=user_data.get("avatar_url"),
                email_verified=email_verified,
            )
        except Exception as e:
            logger.error(f"Failed to exchange GitHub code: {e}")
            raise
        finally:
            await client.aclose()


# Global service instance
oauth_service = OAuthService()
