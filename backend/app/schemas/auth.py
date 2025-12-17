"""Pydantic schemas for authentication API endpoints."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe",
            }
        }


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        }


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing tokens."""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    email_verified: bool = Field(..., description="Whether email is verified")
    full_name: Optional[str] = Field(None, description="User's full name")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    # OAuth connection status
    google_connected: bool = Field(default=False, description="Google account linked")
    github_connected: bool = Field(default=False, description="GitHub account linked")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "email_verified": True,
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "last_login_at": "2024-01-15T10:30:00Z",
                "google_connected": True,
                "github_connected": False,
            }
        }


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    avatar_url: Optional[str] = Field(None, description="User's avatar URL")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Doe",
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request schema for changing password."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewSecure456",
            }
        }


class ForgotPasswordRequest(BaseModel):
    """Request schema for requesting password reset."""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
            }
        }


class ResetPasswordRequest(BaseModel):
    """Request schema for resetting password with token."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "NewSecure789",
            }
        }


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
            }
        }


class OAuthUrlResponse(BaseModel):
    """Response schema for OAuth authorization URL."""

    authorization_url: str = Field(..., description="URL to redirect user for OAuth")
    state: str = Field(..., description="State parameter for CSRF protection")

    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
                "state": "abc123xyz789",
            }
        }


class OAuthCallbackRequest(BaseModel):
    """Request schema for OAuth callback."""

    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State parameter for CSRF verification")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "4/0AX4XfWh...",
                "state": "abc123xyz789",
            }
        }


class OAuthProvidersResponse(BaseModel):
    """Response schema for available OAuth providers."""

    google: bool = Field(..., description="Whether Google OAuth is configured")
    github: bool = Field(..., description="Whether GitHub OAuth is configured")

    class Config:
        json_schema_extra = {
            "example": {
                "google": True,
                "github": True,
            }
        }
