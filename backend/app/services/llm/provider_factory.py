"""Factory for creating LLM provider instances."""
from typing import Optional
from loguru import logger

from app.services.llm.base import BaseLLMProvider
from app.services.llm.google_provider import GoogleGeminiProvider
from app.models.settings import LLMProviderConfig
from app.core.config import settings as app_settings


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    # Registry of supported providers
    _providers = {
        "google": GoogleGeminiProvider,
        "gemini": GoogleGeminiProvider,  # Alias
        # Future providers can be added here:
        # "openai": OpenAIProvider,
        # "anthropic": AnthropicProvider,
    }

    @classmethod
    def create_from_config(
        cls,
        config: LLMProviderConfig,
        temperature: float = 0.7,
    ) -> BaseLLMProvider:
        """
        Create an LLM provider from configuration.

        Args:
            config: LLM provider configuration
            temperature: Sampling temperature (overrides default)

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider name is not supported

        Example:
            config = LLMProviderConfig(
                name="google",
                api_key="...",
                text_model="gemini-1.5-pro-latest"
            )
            provider = LLMProviderFactory.create_from_config(config)
        """
        provider_name = config.name.lower()

        if provider_name not in cls._providers:
            raise ValueError(
                f"Unsupported LLM provider: {config.name}. "
                f"Supported providers: {', '.join(cls._providers.keys())}"
            )

        provider_class = cls._providers[provider_name]

        logger.info(
            f"Creating {provider_name} provider with model: {config.text_model}"
        )

        return provider_class(
            api_key=config.api_key,
            model=config.text_model,
            temperature=temperature,
        )

    @classmethod
    def create_from_settings(
        cls,
        use_fallback: bool = False,
        temperature: float = 0.7,
    ) -> BaseLLMProvider:
        """
        Create provider from application settings.

        Uses environment variables or database settings to create provider.

        Args:
            use_fallback: If True, use fallback provider instead of primary
            temperature: Sampling temperature

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If no provider is configured

        Example:
            # Uses GOOGLE_API_KEY and DEFAULT_TEXT_MODEL from .env
            provider = LLMProviderFactory.create_from_settings()
        """
        # Determine which provider to use
        if app_settings.default_llm_provider.lower() in ["google", "gemini"]:
            api_key = app_settings.google_api_key
            model = app_settings.default_text_model
            provider_name = "google"
        elif app_settings.default_llm_provider.lower() == "openai":
            # Future: OpenAI support
            raise ValueError("OpenAI provider not yet implemented in Phase 2")
        elif app_settings.default_llm_provider.lower() == "anthropic":
            # Future: Anthropic support
            raise ValueError("Anthropic provider not yet implemented in Phase 2")
        else:
            raise ValueError(
                f"Unknown provider in settings: {app_settings.default_llm_provider}"
            )

        # Validate API key
        if not api_key:
            raise ValueError(
                f"No API key configured for {provider_name}. "
                f"Please set GOOGLE_API_KEY in .env file."
            )

        logger.info(
            f"Creating {provider_name} provider from settings: {model}"
        )

        provider_class = cls._providers[provider_name]
        return provider_class(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

    @classmethod
    def create_from_db_settings(
        cls,
        db_settings,  # AppSettings from database
        use_fallback: bool = False,
        temperature: float = 0.7,
    ) -> BaseLLMProvider:
        """
        Create provider from database settings (AppSettings model).

        Args:
            db_settings: AppSettings instance from database
            use_fallback: If True, use fallback provider instead of primary
            temperature: Sampling temperature

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider is not configured
        """
        # Get the appropriate provider config
        provider_config = db_settings.fallback_llm_provider if use_fallback else db_settings.primary_llm_provider

        if not provider_config:
            raise ValueError("No LLM provider configured in database settings")

        provider_name = provider_config.name
        api_key = provider_config.api_key
        model = provider_config.text_model

        if not api_key:
            raise ValueError(f"No API key configured for {provider_name} in database settings")

        logger.info(f"Creating {provider_name} provider from database settings: {model}")

        if provider_name == "google":
            return cls.create_google_gemini(api_key=api_key, model=model, temperature=temperature)
        elif provider_name == "openai":
            raise ValueError("OpenAI provider not yet implemented")
        elif provider_name == "anthropic":
            raise ValueError("Anthropic provider not yet implemented")
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    @classmethod
    def create_google_gemini(
        cls,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-pro-latest",
        temperature: float = 0.7,
    ) -> GoogleGeminiProvider:
        """
        Convenience method to create a Google Gemini provider.

        Args:
            api_key: Google API key (uses settings if not provided)
            model: Gemini model ID
            temperature: Sampling temperature

        Returns:
            GoogleGeminiProvider instance

        Example:
            provider = LLMProviderFactory.create_google_gemini(
                model="gemini-1.5-flash-latest"
            )
        """
        if not api_key:
            api_key = app_settings.google_api_key

        if not api_key:
            raise ValueError(
                "No Google API key provided. "
                "Pass api_key parameter or set GOOGLE_API_KEY in .env"
            )

        logger.info(f"Creating Google Gemini provider: {model}")

        return GoogleGeminiProvider(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

    @classmethod
    def list_supported_providers(cls) -> list[str]:
        """
        Get list of supported provider names.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
