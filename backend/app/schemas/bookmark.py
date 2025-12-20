"""Pydantic schemas for bookmark API endpoints."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class BookmarkResponse(BaseModel):
    """Response schema for a bookmark."""

    id: str
    story_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkWithStoryResponse(BaseModel):
    """Response schema for a bookmark with story details."""

    id: str
    story_id: str
    story_title: str
    cover_image_url: Optional[str] = None
    format: str
    page_count: int
    owner_name: Optional[str] = None
    share_token: str
    created_at: datetime  # Bookmark creation time
    story_created_at: datetime  # Story creation time

    model_config = ConfigDict(from_attributes=True)


class BookmarkListResponse(BaseModel):
    """Paginated response for bookmark list."""

    bookmarks: List[BookmarkWithStoryResponse]
    total: int
    page: int
    page_size: int


class BookmarkStatusResponse(BaseModel):
    """Response for checking bookmark status."""

    is_bookmarked: bool
    bookmark_id: Optional[str] = None
