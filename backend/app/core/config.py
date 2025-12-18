"""Application configuration using Pydantic settings."""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="StorAI-Booker", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    env: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")

    # Server Settings
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # MongoDB Settings
    mongodb_url: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URL")
    mongodb_db_name: str = Field(default="storai_booker", alias="MONGODB_DB_NAME")

    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Celery Settings
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    # S3/MinIO Settings
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_external_endpoint_url: str | None = Field(default=None, alias="S3_EXTERNAL_ENDPOINT_URL")
    s3_public_url: str | None = Field(default=None, alias="S3_PUBLIC_URL")
    s3_access_key_id: str = Field(default="", alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="", alias="S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = Field(default="storai-booker-images", alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")

    # LLM Provider Settings
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")
    default_text_model: str = Field(default="gpt-4-turbo-preview", alias="DEFAULT_TEXT_MODEL")
    default_image_model: str = Field(default="gemini-2.0-flash-exp", alias="DEFAULT_IMAGE_MODEL")

    # Image Generation Settings
    image_aspect_ratio: str = Field(default="16:9", alias="IMAGE_ASPECT_RATIO")
    image_max_retries: int = Field(default=3, alias="IMAGE_MAX_RETRIES")
    image_generation_timeout: int = Field(default=60, alias="IMAGE_GENERATION_TIMEOUT")
    cover_aspect_ratio: str = Field(default="3:4", alias="COVER_ASPECT_RATIO")
    cover_font_path: str | None = Field(default=None, alias="COVER_FONT_PATH")

    # Story Generation Settings
    default_age_min: int = Field(default=3, alias="DEFAULT_AGE_MIN")
    default_age_max: int = Field(default=12, alias="DEFAULT_AGE_MAX")
    default_retry_limit: int = Field(default=3, alias="DEFAULT_RETRY_LIMIT")
    default_max_concurrent_pages: int = Field(default=5, alias="DEFAULT_MAX_CONCURRENT_PAGES")
    nsfw_filter_enabled: bool = Field(default=True, alias="NSFW_FILTER_ENABLED")

    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], alias="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, alias="CORS_CREDENTIALS")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    # JWT Settings
    jwt_secret_key: str = Field(
        default="jwt-secret-key-change-in-production",
        alias="JWT_SECRET_KEY",
        description="Secret key for signing JWT tokens"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # OAuth Settings
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")
    oauth_redirect_url: str = Field(
        default="http://localhost:5173/auth/callback",
        alias="OAUTH_REDIRECT_URL",
        description="Frontend URL for OAuth callbacks"
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env == "production"


# Global settings instance
settings = Settings()
