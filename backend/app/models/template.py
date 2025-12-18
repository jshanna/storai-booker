"""Story template MongoDB document model."""
from datetime import datetime, timezone
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING


class TemplateGenerationInputs(BaseModel):
    """Pre-filled generation inputs for a template.

    Mirrors GenerationInputs from storybook.py for seamless form pre-fill.
    """

    audience_age: int = Field(..., ge=0, le=100, description="Suggested target age")
    audience_gender: Optional[str] = Field(None, description="Target gender if specific")
    topic: str = Field(..., min_length=1, max_length=200, description="Story topic")
    setting: str = Field(..., min_length=1, max_length=200, description="Story setting")
    format: str = Field(default="storybook", pattern="^(storybook|comic)$")
    illustration_style: str = Field(..., min_length=1, max_length=100)
    characters: List[str] = Field(default_factory=list, description="Suggested characters")
    page_count: int = Field(default=10, ge=1, le=50)
    panels_per_page: Optional[int] = Field(None, ge=1, le=9)


class Template(Document):
    """Story template document model.

    Templates are system-wide pre-made story starting points.
    They provide inspiration and quick-start options for story generation.
    """

    # Core fields
    name: Indexed(str) = Field(..., description="Template display name")  # type: ignore
    description: str = Field(..., max_length=300, description="Short description for UI")

    # Template content - mirrors GenerationInputs for form pre-fill
    generation_inputs: TemplateGenerationInputs

    # Metadata for filtering/sorting
    age_range_min: int = Field(..., ge=0, le=100, description="Minimum recommended age")
    age_range_max: int = Field(..., ge=0, le=100, description="Maximum recommended age")
    category: str = Field(..., description="Category: fantasy, adventure, animals, educational")
    tags: List[str] = Field(default_factory=list, description="Additional tags for search")

    # Display
    icon: Optional[str] = Field(None, description="Emoji icon for display")
    cover_image_url: Optional[str] = Field(None, description="Optional preview image URL")
    sort_order: int = Field(default=0, description="Display order (lower = first)")

    # System fields
    is_active: bool = Field(default=True, description="Whether template is visible")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        """Beanie document settings."""

        name = "templates"
        indexes = [
            IndexModel([("is_active", ASCENDING), ("sort_order", ASCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("age_range_min", ASCENDING), ("age_range_max", ASCENDING)]),
            IndexModel([("name", "text"), ("description", "text"), ("tags", "text")]),
        ]
