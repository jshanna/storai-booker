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


class DialogueEntry(BaseModel):
    """A single dialogue bubble in a comic panel."""

    character: str = Field(..., description="Character name speaking")
    text: str = Field(..., description="Dialogue text")
    position: str = Field(
        default="top-left",
        pattern="^(top-left|top-center|top-right|middle-left|middle-right|bottom-left|bottom-center|bottom-right)$",
        description="Position of speech bubble in panel"
    )
    style: str = Field(
        default="speech",
        pattern="^(speech|thought|shout|whisper)$",
        description="Bubble style"
    )


class SoundEffect(BaseModel):
    """A sound effect in a comic panel."""

    text: str = Field(..., description="Sound effect text (e.g., BOOM!, POW!)")
    position: str = Field(
        default="top-right",
        pattern="^(top-left|top-center|top-right|middle-left|middle-center|middle-right|bottom-left|bottom-center|bottom-right)$",
        description="Position in panel"
    )
    style: str = Field(
        default="impact",
        pattern="^(impact|whoosh|ambient|dramatic)$",
        description="Visual style of the effect"
    )


class Panel(BaseModel):
    """A single panel in a comic page."""

    panel_number: int = Field(..., ge=1, le=9, description="Panel number on page")
    illustration_url: Optional[str] = None
    illustration_prompt: Optional[str] = None
    dialogue: List[DialogueEntry] = Field(default_factory=list, description="Speech/thought bubbles")
    caption: Optional[str] = Field(None, description="Narrator text box")
    sound_effects: List[SoundEffect] = Field(default_factory=list, description="Sound effect overlays")
    aspect_ratio: str = Field(default="1:1", description="Panel aspect ratio")
    generation_attempts: int = Field(default=0)
    validated: bool = Field(default=False)


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
    """Storybook or comic page."""

    page_number: int
    # Storybook format fields
    text: Optional[str] = None
    illustration_prompt: Optional[str] = None
    illustration_url: Optional[str] = None
    # Comic format fields
    panels: List[Panel] = Field(default_factory=list, description="Comic panels (empty for storybook)")
    layout: Optional[str] = Field(None, description="Panel layout e.g. '2x2', '3x1', '1-2-1'")
    # Common fields
    generation_attempts: int = Field(default=0)
    validated: bool = Field(default=False)


class Storybook(Document):
    """Storybook document model."""

    # User ownership
    user_id: Indexed(str) = Field(..., description="Owner user ID")  # type: ignore

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
            # User-scoped indexes (most queries will filter by user_id)
            IndexModel([("user_id", 1), ("created_at", DESCENDING)]),
            IndexModel([("user_id", 1), ("status", 1)]),
            IndexModel([("user_id", 1), ("generation_inputs.format", 1)]),
            IndexModel([("user_id", 1), ("status", 1), ("created_at", DESCENDING)]),
            IndexModel([("user_id", 1), ("generation_inputs.format", 1), ("created_at", DESCENDING)]),
            # Single field indexes for admin queries
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("status", 1)]),
            IndexModel([("title", "text")]),  # Text search on title
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
