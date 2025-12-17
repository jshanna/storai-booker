"""Storybook MongoDB document models using Beanie ODM."""
from datetime import datetime, timezone
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field, ConfigDict
from pymongo import IndexModel, DESCENDING


class GenerationInputs(BaseModel):
    """User inputs for story generation."""

    audience_age: int = Field(..., ge=0, le=100, description="Target audience age")
    audience_gender: Optional[str] = Field(None, description="Target audience gender")
    topic: str = Field(..., min_length=1, max_length=200, description="Story topic")
    setting: str = Field(..., min_length=1, max_length=200, description="Story setting")
    format: str = Field(default="storybook", pattern="^(storybook|comic)$", description="Story format")
    illustration_style: str = Field(..., min_length=1, max_length=100, description="Illustration style")
    characters: List[str] = Field(default_factory=list, description="User-described characters")
    page_count: int = Field(..., ge=1, le=50, description="Number of pages")
    panels_per_page: Optional[int] = Field(None, ge=1, le=9, description="Panels per page for comics")


class CharacterDescription(BaseModel):
    """Expanded character description."""

    name: str
    physical_description: str
    personality: str
    role: str  # protagonist, sidekick, villain, etc.


class StoryMetadata(BaseModel):
    """Story generation metadata."""

    title: Optional[str] = None
    character_descriptions: List[CharacterDescription] = Field(default_factory=list)
    character_sheet_urls: List[str] = Field(default_factory=list, description="URLs to character reference sheets")
    character_relations: Optional[str] = None
    story_outline: Optional[str] = None
    page_outlines: List[str] = Field(default_factory=list)
    illustration_style_guide: Optional[str] = None


class Page(BaseModel):
    """Storybook page."""

    page_number: int
    text: Optional[str] = None  # For storybook format
    illustration_prompt: Optional[str] = None  # For storybook format
    illustration_url: Optional[str] = None  # For storybook format
    generation_attempts: int = Field(default=0)
    validated: bool = Field(default=False)


class Storybook(Document):
    """Storybook document model."""

    title: Indexed(str) = Field(..., description="Story title")  # type: ignore
    created_at: Indexed(datetime) = Field(default_factory=lambda: datetime.now(timezone.utc))  # type: ignore
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generation_inputs: GenerationInputs
    metadata: StoryMetadata = Field(default_factory=StoryMetadata)
    pages: List[Page] = Field(default_factory=list)
    status: str = Field(default="pending", pattern="^(pending|generating|complete|error)$")
    error_message: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Settings:
        """Beanie document settings."""

        name = "storybooks"
        indexes = [
            # Single field indexes
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("generation_inputs.format", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("title", "text")]),  # Text search on title
            # Compound indexes for common filter combinations
            IndexModel([("status", 1), ("created_at", DESCENDING)]),
            IndexModel([("generation_inputs.format", 1), ("created_at", DESCENDING)]),
            IndexModel([("status", 1), ("generation_inputs.format", 1), ("created_at", DESCENDING)]),
        ]
        # Configure Beanie to use timezone-aware datetimes
        use_state_management = True
        validate_on_save = True

    model_config = ConfigDict(
        json_schema_extra={
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
                "status": "complete",
            }
        }
    )
