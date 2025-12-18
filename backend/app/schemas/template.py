"""Pydantic schemas for template API endpoints."""
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.template import TemplateGenerationInputs


class TemplateResponse(BaseModel):
    """Response schema for a single template."""

    id: str
    name: str
    description: str
    generation_inputs: TemplateGenerationInputs
    age_range_min: int
    age_range_max: int
    category: str
    tags: List[str]
    icon: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response schema for listing templates."""

    templates: List[TemplateResponse]
    total: int


class TemplateCategoriesResponse(BaseModel):
    """Response schema for listing template categories."""

    categories: List[str]
