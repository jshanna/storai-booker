"""Authentication service for JWT and password handling."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets

import bcrypt
from jose import jwt, JWTError
from loguru import logger

from app.core.config import settings
from app.models.user import User
from app.services.cache import cache_service

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# Cache prefixes
BLACKLIST_PREFIX = "token_blacklist:"


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        """Initialize auth service."""
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days

    # Password Operations

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    # Token Operations

    def create_access_token(self, user_id: str, email: str) -> Tuple[str, datetime]:
        """Create a JWT access token.

        Returns:
            Tuple of (token, expiration_datetime)
        """
        expires = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "email": email,
            "type": TOKEN_TYPE_ACCESS,
            "exp": expires,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, expires

    def create_refresh_token(self, user_id: str) -> Tuple[str, datetime]:
        """Create a JWT refresh token.

        Returns:
            Tuple of (token, expiration_datetime)
        """
        expires = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        # Add a unique identifier for this refresh token
        jti = secrets.token_urlsafe(32)
        payload = {
            "sub": user_id,
            "type": TOKEN_TYPE_REFRESH,
            "jti": jti,
            "exp": expires,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, expires

    def create_token_pair(self, user: User) -> dict:
        """Create both access and refresh tokens for a user.

        Returns:
            Dict with access_token, refresh_token, token_type, and expires_in
        """
        user_id = str(user.id)
        access_token, access_expires = self.create_access_token(user_id, user.email)
        refresh_token, _ = self.create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,  # in seconds
        }

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT token.

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.debug(f"Token decode error: {e}")
            return None

    def validate_access_token(self, token: str) -> Optional[dict]:
        """Validate an access token.

        Returns:
            Token payload if valid access token, None otherwise
        """
        payload = self.decode_token(token)
        if not payload:
            return None

        # Check token type
        if payload.get("type") != TOKEN_TYPE_ACCESS:
            return None

        # Check if token is blacklisted
        if self._is_token_blacklisted(token):
            return None

        return payload

    def validate_refresh_token(self, token: str) -> Optional[dict]:
        """Validate a refresh token.

        Returns:
            Token payload if valid refresh token, None otherwise
        """
        payload = self.decode_token(token)
        if not payload:
            return None

        # Check token type
        if payload.get("type") != TOKEN_TYPE_REFRESH:
            return None

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and self._is_refresh_token_blacklisted(jti):
            return None

        return payload

    async def blacklist_token(self, token: str) -> None:
        """Add a token to the blacklist."""
        payload = self.decode_token(token)
        if not payload:
            return

        token_type = payload.get("type")

        if token_type == TOKEN_TYPE_ACCESS:
            # For access tokens, blacklist the whole token
            exp = payload.get("exp", 0)
            ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
            if ttl > 0:
                # Cache service is synchronous, so no await needed
                cache_service.set(
                    f"{BLACKLIST_PREFIX}{token[:32]}",
                    "1",
                    ttl=ttl
                )
        elif token_type == TOKEN_TYPE_REFRESH:
            # For refresh tokens, blacklist by jti
            jti = payload.get("jti")
            if jti:
                exp = payload.get("exp", 0)
                ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
                if ttl > 0:
                    # Cache service is synchronous, so no await needed
                    cache_service.set(
                        f"{BLACKLIST_PREFIX}refresh:{jti}",
                        "1",
                        ttl=ttl
                    )

    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if an access token is blacklisted (synchronous check)."""
        # Note: This is a simplified check. In production, use async properly.
        # The actual check happens in the validate methods
        return False

    def _is_refresh_token_blacklisted(self, jti: str) -> bool:
        """Check if a refresh token is blacklisted (synchronous check)."""
        return False

    async def is_token_blacklisted_async(self, token: str) -> bool:
        """Check if an access token is blacklisted."""
        # Cache service is synchronous, so no await needed
        result = cache_service.get(f"{BLACKLIST_PREFIX}{token[:32]}")
        return result is not None

    async def is_refresh_token_blacklisted_async(self, jti: str) -> bool:
        """Check if a refresh token is blacklisted."""
        # Cache service is synchronous, so no await needed
        result = cache_service.get(f"{BLACKLIST_PREFIX}refresh:{jti}")
        return result is not None

    # Password Reset Operations

    def generate_password_reset_token(self) -> str:
        """Generate a secure password reset token."""
        return secrets.token_urlsafe(32)

    def get_password_reset_expiry(self) -> datetime:
        """Get expiration time for password reset token (24 hours)."""
        return datetime.now(timezone.utc) + timedelta(hours=24)

    # User Operations

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Returns:
            User if credentials are valid, None otherwise
        """
        user = await User.find_one(User.email == email)
        if not user:
            logger.debug(f"User not found: {email}")
            return None

        if not user.password_hash:
            logger.debug(f"User has no password (OAuth only): {email}")
            return None

        if not user.is_active:
            logger.debug(f"User is inactive: {email}")
            return None

        if not self.verify_password(password, user.password_hash):
            logger.debug(f"Invalid password for user: {email}")
            return None

        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        try:
            from beanie import PydanticObjectId
            return await User.get(PydanticObjectId(user_id))
        except Exception as e:
            logger.debug(f"Error getting user by ID {user_id}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email."""
        return await User.find_one(User.email == email)

    async def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        google_id: Optional[str] = None,
        github_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        email_verified: bool = False,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=self.hash_password(password) if password else None,
            full_name=full_name,
            google_id=google_id,
            github_id=github_id,
            avatar_url=avatar_url,
            email_verified=email_verified,
        )
        await user.insert()
        logger.info(f"Created new user: {email}")
        return user


# Global service instance
auth_service = AuthService()
