"""Pydantic schemas for comment API endpoints."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CommentCreateRequest(BaseModel):
    """Request schema for creating a comment."""

    text: str = Field(..., min_length=1, max_length=2000, description="Comment text")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "What a wonderful story! My kids loved it."
            }
        }
    )


class CommentResponse(BaseModel):
    """Response schema for a comment."""

    id: str
    story_id: str
    user_id: str
    author_name: str
    author_avatar_url: Optional[str] = None
    text: str
    created_at: datetime
    updated_at: datetime
    is_edited: bool

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    """Response schema for listing comments."""

    comments: List[CommentResponse]
    total: int
    page: int
    page_size: int
