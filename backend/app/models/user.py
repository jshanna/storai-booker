"""User MongoDB document model."""
from datetime import datetime, timezone
from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pymongo import IndexModel, ASCENDING


class UserPreferences(BaseModel):
    """User preferences for story generation."""

    default_format: str = Field(default="storybook", pattern="^(storybook|comic)$")
    default_illustration_style: str = Field(default="cartoon")
    default_page_count: int = Field(default=10, ge=1, le=50)
    theme: str = Field(default="system", pattern="^(light|dark|system)$")


class User(Document):
    """User document model."""

    # Core fields
    email: Indexed(str, unique=True) = Field(..., description="User email address")  # type: ignore
    email_verified: bool = Field(default=False)
    password_hash: Optional[str] = Field(default=None, description="Null for OAuth-only users")

    # Profile
    full_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None)

    # Account status
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    # OAuth provider IDs (null if not linked)
    google_id: Optional[str] = Field(default=None)
    github_id: Optional[str] = Field(default=None)

    # User preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = Field(default=None)

    # Password reset
    password_reset_token: Optional[str] = Field(default=None)
    password_reset_expires: Optional[datetime] = Field(default=None)

    class Settings:
        """Beanie document settings."""

        name = "users"
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("google_id", ASCENDING)], sparse=True),
            IndexModel([("github_id", ASCENDING)], sparse=True),
            IndexModel([("created_at", ASCENDING)]),
        ]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "email_verified": False,
                "full_name": "John Doe",
                "is_active": True,
                "preferences": {
                    "default_format": "storybook",
                    "default_illustration_style": "cartoon",
                    "default_page_count": 10,
                    "theme": "system",
                },
            }
        }
    )

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def record_login(self) -> None:
        """Record a login event."""
        self.last_login_at = datetime.now(timezone.utc)
        self.update_timestamp()
