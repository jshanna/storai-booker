"""Pydantic schemas for settings API endpoints."""
from typing import Optional
from pydantic import BaseModel, Field

from app.models.settings import (
    AgeRangeSettings,
    ContentFilterSettings,
    GenerationLimits,
    LLMProviderConfig,
    DefaultSettings,
)


class SettingsUpdateRequest(BaseModel):
    """Request schema for updating settings."""

    age_range: Optional[AgeRangeSettings] = None
    content_filters: Optional[ContentFilterSettings] = None
    generation_limits: Optional[GenerationLimits] = None
    primary_llm_provider: Optional[LLMProviderConfig] = None
    fallback_llm_provider: Optional[LLMProviderConfig] = None
    defaults: Optional[DefaultSettings] = None

    class Config:
        json_schema_extra = {
            "example": {
                "age_range": {"min": 5, "max": 12, "enforce": True},
                "primary_llm_provider": {
                    "name": "openai",
                    "api_key": "sk-...",
                    "text_model": "gpt-4-turbo-preview",
                    "image_model": "dall-e-3",
                },
            }
        }


class SettingsResponse(BaseModel):
    """Response schema for settings."""

    id: str
    user_id: str
    age_range: AgeRangeSettings
    content_filters: ContentFilterSettings
    generation_limits: GenerationLimits
    primary_llm_provider: LLMProviderConfig
    fallback_llm_provider: Optional[LLMProviderConfig] = None
    defaults: DefaultSettings

    class Config:
        from_attributes = True
