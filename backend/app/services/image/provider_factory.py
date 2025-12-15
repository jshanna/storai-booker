"""Factory for creating image generation providers."""

from typing import Literal

from loguru import logger

from app.core.config import settings
from app.services.image.base import BaseImageProvider
from app.services.image.google_imagen import GoogleImagenProvider


ImageProviderType = Literal["google"]


class ImageProviderFactory:
    """Factory for creating image generation providers based on configuration."""

    @staticmethod
    def create_google_imagen(
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        aspect_ratio: str = "16:9",
        temperature: float = 1.0,
    ) -> GoogleImagenProvider:
        """
        Create Google Gemini image generation provider.

        Args:
            api_key: Google API key
            model: Gemini model name
            aspect_ratio: Default aspect ratio
            temperature: Sampling temperature

        Returns:
            Configured GoogleImagenProvider instance

        Raises:
            ValueError: If API key is empty
        """
        if not api_key:
            raise ValueError("Google API key is required")

        logger.info(f"Creating Google Imagen provider with model: {model}")
        return GoogleImagenProvider(
            api_key=api_key,
            model=model,
            aspect_ratio=aspect_ratio,
            temperature=temperature,
        )

    @staticmethod
    def create_from_settings(
        provider: str | None = None,
        model: str | None = None,
    ) -> BaseImageProvider:
        """
        Create image provider from application settings.

        Uses settings from .env file to determine which provider to use
        and configure it with the appropriate API keys.

        Args:
            provider: Override default provider from settings (default: None)
            model: Override default model from settings (default: None)

        Returns:
            Configured image provider instance

        Raises:
            ValueError: If provider is unsupported or API key is missing
        """
        # Use settings or override
        provider_name = provider or "google"  # Only Google supported for now
        model_name = model or settings.default_image_model

        logger.info(f"Creating image provider: {provider_name} with model: {model_name}")

        if provider_name == "google":
            if not settings.google_api_key:
                raise ValueError(
                    "Google API key not configured. Set GOOGLE_API_KEY in .env"
                )

            return ImageProviderFactory.create_google_imagen(
                api_key=settings.google_api_key,
                model=model_name,
                aspect_ratio=settings.image_aspect_ratio,
                temperature=1.0,  # Use high temperature for creative images
            )
        else:
            raise ValueError(
                f"Unsupported image provider: {provider_name}. "
                f"Supported providers: google"
            )
