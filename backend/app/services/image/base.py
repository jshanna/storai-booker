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
        target_age: Optional[int] = None,
        **kwargs
    ) -> bytes:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Override default aspect ratio (e.g., "16:9", "3:4", "1:1")
            negative_prompt: Optional negative prompt (what to avoid)
            target_age: Target audience age (affects content guidelines)
            **kwargs: Additional provider-specific parameters

        Returns:
            PNG image data as bytes

        Raises:
            Exception: If image generation fails
        """
        pass

    def _enhance_prompt_for_audience(self, prompt: str, target_age: Optional[int] = None) -> str:
        """
        Enhance a prompt with age-appropriate content guidelines.

        Adds safety guidelines and style enhancements based on the target
        audience age.

        Args:
            prompt: Original image prompt
            target_age: Target audience age (default assumes children if not specified)

        Returns:
            Enhanced prompt with appropriate guidelines
        """
        age = target_age or 8  # Default to child-appropriate if not specified

        if age <= 6:
            # Very young children - most restrictive
            safety_prefix = (
                "Create a gentle, child-friendly illustration for very young children (ages 3-6). "
                "Style: soft colors, simple shapes, friendly characters, non-scary. "
            )
            safety_suffix = (
                " Use soft, pastel colors. Absolutely nothing frightening, intense, or complex. "
                "The image should feel safe, warm, and nurturing. Simple and cheerful."
            )
        elif age <= 12:
            # Children - standard children's content
            safety_prefix = (
                "Create a child-friendly, wholesome illustration suitable for children. "
                "Style: colorful, friendly, age-appropriate for kids. "
            )
            safety_suffix = (
                " Use bright, cheerful colors. Avoid anything frightening, violent, or inappropriate. "
                "The image should feel warm, inviting, and magical."
            )
        elif age <= 17:
            # Teens - more mature themes allowed but still appropriate
            safety_prefix = (
                "Create an engaging illustration suitable for teenagers. "
                "Style: dynamic, stylish, age-appropriate for teens. "
            )
            safety_suffix = (
                " The image can have more dramatic elements but should remain appropriate "
                "for a teen audience. No explicit content, gore, or extreme violence."
            )
        else:
            # Adults - minimal restrictions, focus on quality
            safety_prefix = (
                "Create a high-quality illustration. "
                "Style: professional, artistic, visually compelling. "
            )
            safety_suffix = (
                " Focus on artistic quality and visual impact. "
                "The image should be sophisticated and well-composed."
            )

        return f"{safety_prefix}{prompt}{safety_suffix}"

    # Keep old method name for backwards compatibility
    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """Deprecated: Use _enhance_prompt_for_audience instead."""
        return self._enhance_prompt_for_audience(prompt, target_age=8)
