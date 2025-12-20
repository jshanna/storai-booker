"""Pydantic schemas for story sharing API endpoints."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.storybook import GenerationInputs, StoryMetadata
from app.schemas.story import PageResponse


class ShareResponse(BaseModel):
    """Response schema for enabling sharing on a story."""

    story_id: str
    is_shared: bool
    share_token: Optional[str] = None
    share_url: Optional[str] = None
    shared_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SharedStoryResponse(BaseModel):
    """Response schema for a publicly shared story."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    generation_inputs: GenerationInputs
    metadata: StoryMetadata
    pages: List[PageResponse]
    status: str
    cover_image_url: Optional[str] = None
    # Sharing info
    is_shared: bool = True
    shared_at: Optional[datetime] = None
    # Owner info (optional, for display)
    owner_name: Optional[str] = Field(default=None, description="Story owner's display name")

    model_config = ConfigDict(from_attributes=True)


class PublicStoryListItem(BaseModel):
    """Minimal response schema for a story in the public browse list."""

    id: str
    title: str
    cover_image_url: Optional[str] = None
    format: str = Field(..., description="Story format: storybook or comic")
    page_count: int = Field(..., description="Number of pages in the story")
    owner_name: Optional[str] = None
    share_token: str
    shared_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicStoriesListResponse(BaseModel):
    """Paginated response for public stories browse."""

    stories: List[PublicStoryListItem]
    total: int
    page: int
    page_size: int
