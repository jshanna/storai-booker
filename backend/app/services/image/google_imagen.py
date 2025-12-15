"""Google Gemini image generation provider."""

import asyncio
import base64
from typing import Optional

import google.generativeai as genai
from loguru import logger

from app.services.image.base import BaseImageProvider


class GoogleImagenProvider(BaseImageProvider):
    """
    Google Gemini image generation provider.

    Uses Google's Gemini models (e.g., gemini-2.0-flash-exp) to generate
    images from text prompts.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp",
        aspect_ratio: str = "16:9",
        temperature: float = 1.0,
    ):
        """
        Initialize Google Imagen provider.

        Args:
            api_key: Google API key
            model: Gemini model name (must support image generation)
            aspect_ratio: Default aspect ratio
            temperature: Sampling temperature
        """
        super().__init__(api_key, model, aspect_ratio, temperature)
        genai.configure(api_key=self.api_key)
        self._client = None

    def _get_client(self) -> genai.GenerativeModel:
        """
        Get or create Gemini client.

        Returns:
            Configured GenerativeModel instance
        """
        if self._client is None:
            self._client = genai.GenerativeModel(
                self.model,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                ),
            )
        return self._client

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Generate an image using Google Gemini.

        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Aspect ratio (e.g., "16:9", "3:4", "1:1")
            negative_prompt: Not used for Gemini (kept for interface compatibility)
            **kwargs: Additional parameters

        Returns:
            PNG image data as bytes

        Raises:
            Exception: If image generation fails
        """
        try:
            # Use provided aspect ratio or default
            ratio = aspect_ratio or self.aspect_ratio

            # Enhance prompt for children's content
            enhanced_prompt = self._enhance_prompt_for_children(prompt)

            # Add aspect ratio instruction to prompt
            final_prompt = f"{enhanced_prompt}\n\nAspect ratio: {ratio}"

            logger.info(f"Generating image with Gemini model: {self.model}")
            logger.debug(f"Prompt: {final_prompt[:200]}...")

            # Generate image using Gemini
            client = self._get_client()

            # Gemini image generation requires specifying output modality
            # Note: This API might vary by version - adjust as needed
            response = await asyncio.to_thread(
                client.generate_content,
                final_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    # Gemini 2.0 supports image generation
                    # The exact parameter name might vary
                    candidate_count=1,
                ),
            )

            # Extract image from response
            # Gemini returns images in response.parts
            if not response.parts:
                raise ValueError("No content returned from Gemini")

            # Look for image data in response parts
            image_data = None
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Image is in inline_data.data (base64 or bytes)
                    inline_data = part.inline_data
                    if hasattr(inline_data, 'data'):
                        image_data = inline_data.data
                        break

            if image_data is None:
                # If no inline data, try to extract from text response
                # Some models might return base64 in text
                text = response.text if hasattr(response, 'text') else str(response)
                if 'base64' in text.lower():
                    # Try to extract base64 data
                    logger.warning("Image returned as base64 text, attempting to decode")
                    # This is a fallback - adjust based on actual API response
                    raise ValueError("Image generation returned text instead of binary data")
                else:
                    raise ValueError(f"No image data found in response: {text[:200]}")

            # Convert to bytes if needed
            if isinstance(image_data, str):
                # Base64 encoded
                image_bytes = base64.b64decode(image_data)
            elif isinstance(image_data, bytes):
                # Already bytes
                image_bytes = image_data
            else:
                raise ValueError(f"Unexpected image data type: {type(image_data)}")

            logger.info(f"Successfully generated image ({len(image_bytes)} bytes)")
            return image_bytes

        except Exception as e:
            logger.error(f"Failed to generate image with Gemini: {e}")
            raise

    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """
        Override to add Gemini-specific enhancements.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt for children's content
        """
        # Call base implementation
        base_enhanced = super()._enhance_prompt_for_children(prompt)

        # Add Gemini-specific instructions
        gemini_specific = (
            " Create as a digital illustration in PNG format. "
            "High quality, detailed, professional children's book illustration style."
        )

        return f"{base_enhanced}{gemini_specific}"
