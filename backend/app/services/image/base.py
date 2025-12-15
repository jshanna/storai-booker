"""Base class for image generation providers."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseImageProvider(ABC):
    """
    Abstract base class for image generation providers.

    Provides a common interface for generating images from text prompts
    across different AI image generation services.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        aspect_ratio: str = "16:9",
        temperature: float = 1.0,
    ):
        """
        Initialize image provider.

        Args:
            api_key: API key for the image generation service
            model: Model name to use for generation
            aspect_ratio: Default aspect ratio for generated images (e.g., "16:9", "3:4")
            temperature: Sampling temperature (0.0-1.0, higher = more creative)
        """
        self.api_key = api_key
        self.model = model
        self.aspect_ratio = aspect_ratio
        self.temperature = temperature

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Override default aspect ratio (e.g., "16:9", "3:4", "1:1")
            negative_prompt: Optional negative prompt (what to avoid)
            **kwargs: Additional provider-specific parameters

        Returns:
            PNG image data as bytes

        Raises:
            Exception: If image generation fails
        """
        pass

    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """
        Enhance a prompt to ensure child-appropriate content.

        Adds safety guidelines and style enhancements to ensure
        generated images are suitable for children's storybooks.

        Args:
            prompt: Original image prompt

        Returns:
            Enhanced prompt with safety guidelines
        """
        safety_prefix = (
            "Create a child-friendly, wholesome illustration suitable for young children. "
            "Style: colorful, friendly, non-scary, age-appropriate. "
        )

        safety_suffix = (
            " Use bright, cheerful colors. Avoid anything frightening, violent, or inappropriate. "
            "The image should feel warm, inviting, and magical."
        )

        return f"{safety_prefix}{prompt}{safety_suffix}"
