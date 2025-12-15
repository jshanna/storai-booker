"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for the provider
            model: Model identifier (e.g., 'gemini-1.5-pro-latest', 'gpt-4')
            temperature: Sampling temperature (0.0-1.0), higher = more creative
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._client: Optional[Any] = None

    @abstractmethod
    def get_client(self) -> Any:
        """
        Get or create the LLM client instance.

        Returns:
            LangChain LLM client

        Note:
            Implementations should cache the client in self._client
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Text prompt for generation
            max_tokens: Maximum tokens to generate (optional)
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text string

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output matching a Pydantic model.

        Args:
            prompt: Text prompt for generation
            response_model: Pydantic model class for output structure
            **kwargs: Additional provider-specific parameters

        Returns:
            Instance of response_model populated with generated data

        Raises:
            ValidationError: If output doesn't match schema
            Exception: If generation fails

        Example:
            class Story(BaseModel):
                title: str
                content: str

            result = await provider.generate_structured(
                "Write a story about...",
                Story
            )
            print(result.title)  # Access typed field
        """
        pass

    def __repr__(self) -> str:
        """String representation of provider."""
        return f"{self.__class__.__name__}(model='{self.model}', temperature={self.temperature})"
