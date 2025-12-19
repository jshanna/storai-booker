"""Comment MongoDB document model for story sharing."""
from datetime import datetime, timezone
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field, ConfigDict
from pymongo import IndexModel, DESCENDING


class Comment(Document):
    """Comment document model for shared stories."""

    # References
    story_id: Indexed(str) = Field(..., description="ID of the story being commented on")  # type: ignore
    user_id: Indexed(str) = Field(..., description="ID of the comment author")  # type: ignore

    # Author info (denormalized for display without user lookup)
    author_name: str = Field(..., max_length=100, description="Author display name")
    author_avatar_url: Optional[str] = Field(default=None, description="Author avatar URL")

    # Content
    text: str = Field(..., min_length=1, max_length=2000, description="Comment text")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Metadata
    is_edited: bool = Field(default=False, description="Whether comment has been edited")

    class Settings:
        """Beanie document settings."""

        name = "comments"
        indexes = [
            # For listing comments on a story (sorted by newest first)
            IndexModel([("story_id", 1), ("created_at", DESCENDING)]),
            # For finding user's comments
            IndexModel([("user_id", 1)]),
            # For cleanup when story is deleted
            IndexModel([("story_id", 1)]),
        ]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "author_name": "John Doe",
                "author_avatar_url": "https://example.com/avatar.jpg",
                "text": "What a wonderful story! My kids loved it.",
                "is_edited": False,
            }
        }
    )

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp and mark as edited."""
        self.updated_at = datetime.now(timezone.utc)
        self.is_edited = True
