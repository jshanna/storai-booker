"""Application settings MongoDB document model."""
from typing import Optional
from beanie import Document
from pydantic import BaseModel, Field


class AgeRangeSettings(BaseModel):
    """Age range restriction settings."""

    min: int = Field(default=3, ge=0, le=100)
    max: int = Field(default=12, ge=0, le=100)
    enforce: bool = Field(default=True)


class ContentFilterSettings(BaseModel):
    """Content filter settings."""

    nsfw_filter: bool = Field(default=True)
    violence_level: str = Field(default="low", pattern="^(none|low|medium|high)$")
    scary_content: bool = Field(default=False)


class SafetySettings(BaseModel):
    """AI safety filter settings for LLM providers."""

    # Safety threshold: controls how strict safety filters are
    # Options: "block_none", "block_only_high", "block_medium_and_above", "block_low_and_above"
    safety_threshold: str = Field(
        default="block_medium_and_above",
        pattern="^(block_none|block_only_high|block_medium_and_above|block_low_and_above)$",
        description="Safety filter threshold for AI providers"
    )

    # Allow adult content in generated images (18+ characters)
    allow_adult_imagery: bool = Field(
        default=False,
        description="Allow adult characters in image generation"
    )

    # Bypass safety filters entirely (use with caution)
    bypass_safety_filters: bool = Field(
        default=False,
        description="Completely disable AI safety filters (not recommended)"
    )


class GenerationLimits(BaseModel):
    """Generation limit settings."""

    retry_limit: int = Field(default=3, ge=1, le=10)
    max_concurrent_pages: int = Field(default=5, ge=1, le=20)
    timeout_seconds: int = Field(default=300, ge=30, le=1800)


class LLMProviderConfig(BaseModel):
    """LLM provider configuration."""

    name: str = Field(..., description="Provider name (openai, anthropic, google)")
    api_key: str = Field(default="", description="API key (encrypted)")
    endpoint: Optional[str] = Field(None, description="Custom API endpoint")
    text_model: str = Field(default="gpt-4-turbo-preview", description="Text generation model")
    image_model: str = Field(default="dall-e-3", description="Image generation model")


class DefaultSettings(BaseModel):
    """Default generation settings."""

    format: str = Field(default="storybook", pattern="^(storybook|comic)$")
    illustration_style: str = Field(default="cartoon")
    page_count: int = Field(default=10, ge=1, le=50)
    panels_per_page: int = Field(default=4, ge=1, le=9)


class AppSettings(Document):
    """Application settings document."""

    user_id: Optional[str] = Field(default="default", description="User ID (for future multi-user support)")
    age_range: AgeRangeSettings = Field(default_factory=AgeRangeSettings)
    content_filters: ContentFilterSettings = Field(default_factory=ContentFilterSettings)
    safety_settings: SafetySettings = Field(default_factory=SafetySettings)
    generation_limits: GenerationLimits = Field(default_factory=GenerationLimits)
    primary_llm_provider: LLMProviderConfig = Field(
        default_factory=lambda: LLMProviderConfig(name="openai")
    )
    fallback_llm_provider: Optional[LLMProviderConfig] = None
    defaults: DefaultSettings = Field(default_factory=DefaultSettings)

    class Settings:
        """Beanie document settings."""

        name = "app_settings"

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "default",
                "age_range": {"min": 3, "max": 12, "enforce": True},
                "content_filters": {
                    "nsfw_filter": True,
                    "violence_level": "low",
                    "scary_content": False,
                },
                "generation_limits": {
                    "retry_limit": 3,
                    "max_concurrent_pages": 5,
                    "timeout_seconds": 300,
                },
                "primary_llm_provider": {
                    "name": "openai",
                    "text_model": "gpt-4-turbo-preview",
                    "image_model": "dall-e-3",
                },
                "defaults": {
                    "format": "storybook",
                    "illustration_style": "cartoon",
                    "page_count": 10,
                },
            }
        }
