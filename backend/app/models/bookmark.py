"""Bookmark model for saved stories."""
from datetime import datetime, timezone
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel, DESCENDING


class Bookmark(Document):
    """
    Bookmark document for saving stories.

    Allows users to bookmark shared stories for later access.
    """

    user_id: Indexed(str) = Field(..., description="ID of the user who bookmarked")
    story_id: Indexed(str) = Field(..., description="ID of the bookmarked story")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the bookmark was created",
    )

    class Settings:
        name = "bookmarks"
        indexes = [
            # For listing user's bookmarks (newest first)
            IndexModel([("user_id", 1), ("created_at", DESCENDING)]),
            # Unique constraint: one bookmark per user per story
            IndexModel([("user_id", 1), ("story_id", 1)], unique=True),
        ]
