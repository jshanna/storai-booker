"""Pydantic schemas for story API endpoints."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.storybook import GenerationInputs, CharacterDescription, StoryMetadata, Page


class DialogueEntryResponse(BaseModel):
    """Response schema for a dialogue entry in a comic panel."""

    character: str
    text: str
    position: str
    style: str


class SoundEffectResponse(BaseModel):
    """Response schema for a sound effect in a comic panel."""

    text: str
    position: str
    style: str


class PanelResponse(BaseModel):
    """Response schema for a comic panel."""

    panel_number: int
    illustration_url: Optional[str] = None
    illustration_prompt: Optional[str] = None
    dialogue: List[DialogueEntryResponse] = []
    caption: Optional[str] = None
    sound_effects: List[SoundEffectResponse] = []
    aspect_ratio: str = "1:1"
    generation_attempts: int = 0
    validated: bool = False


class StoryCreateRequest(BaseModel):
    """Request schema for creating a new story."""

    title: str = Field(..., min_length=1, max_length=200, description="Story title")
    generation_inputs: GenerationInputs

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Magical Forest Adventure",
                "generation_inputs": {
                    "audience_age": 7,
                    "topic": "A brave squirrel exploring a magical forest",
                    "setting": "Enchanted forest with talking animals",
                    "format": "storybook",
                    "illustration_style": "watercolor",
                    "characters": ["A brave squirrel named Hazel"],
                    "page_count": 10,
                },
            }
        }


class PageResponse(BaseModel):
    """Response schema for a page (storybook or comic)."""

    page_number: int
    # Storybook format fields
    text: Optional[str] = None
    illustration_prompt: Optional[str] = None
    illustration_url: Optional[str] = None
    # Comic format fields
    panels: List[PanelResponse] = []
    layout: Optional[str] = None
    # Common fields
    generation_attempts: int = 0
    validated: bool = False


class StoryResponse(BaseModel):
    """Response schema for a story."""

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    generation_inputs: GenerationInputs
    metadata: StoryMetadata
    pages: List[PageResponse]
    status: str
    error_message: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class StoryListResponse(BaseModel):
    """Response schema for listing stories."""

    stories: List[StoryResponse]
    total: int
    page: int
    page_size: int


class StoryStatusResponse(BaseModel):
    """Response schema for story generation status."""

    id: str
    status: str
    progress: Optional[float] = None  # 0.0 to 1.0
    current_step: Optional[str] = None
    error_message: Optional[str] = None
