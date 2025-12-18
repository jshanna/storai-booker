"""Google Gemini image generation provider using Gemini 2.5 Flash Image."""

import asyncio
from io import BytesIO
from typing import Optional, List
from PIL import Image as PILImage

from google import genai
from google.genai.types import GenerateContentConfig, ImageConfig, SafetySetting, HarmCategory, HarmBlockThreshold
from loguru import logger

from app.services.image.base import BaseImageProvider


class GoogleImagenProvider(BaseImageProvider):
    """
    Google Gemini image generation provider.

    Uses Google's Gemini 2.5 Flash Image model to generate images from text prompts.
    This is a multimodal model that uses the same API as text generation.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash-image",
        aspect_ratio: str = "16:9",
        temperature: float = 1.0,
    ):
        """
        Initialize Google Gemini image provider.

        Args:
            api_key: Google API key
            model: Gemini model name (gemini-2.5-flash-image or gemini-3-pro-preview-image)
            aspect_ratio: Default aspect ratio (1:1, 16:9, 3:4, etc.)
            temperature: Sampling temperature (not used for image generation but kept for interface)
        """
        super().__init__(api_key, model, aspect_ratio, temperature)
        self._client = None

    def _get_client(self) -> genai.Client:
        """
        Get or create Gemini client.

        Returns:
            Configured genai.Client instance
        """
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _map_safety_threshold(self, threshold: str) -> HarmBlockThreshold:
        """
        Map our safety threshold to Gemini's HarmBlockThreshold.

        Args:
            threshold: Our threshold string

        Returns:
            Gemini HarmBlockThreshold enum
        """
        threshold_map = {
            "block_none": HarmBlockThreshold.BLOCK_NONE,
            "block_only_high": HarmBlockThreshold.BLOCK_ONLY_HIGH,
            "block_medium_and_above": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "block_low_and_above": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
        return threshold_map.get(threshold, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE)

    def _build_safety_settings(
        self,
        safety_threshold: str,
        bypass_safety_filters: bool
    ) -> List[SafetySetting]:
        """
        Build Gemini safety settings.

        Args:
            safety_threshold: Safety threshold level
            bypass_safety_filters: Whether to bypass all filters

        Returns:
            List of SafetySetting objects
        """
        if bypass_safety_filters:
            threshold = HarmBlockThreshold.BLOCK_NONE
        else:
            threshold = self._map_safety_threshold(safety_threshold)

        # Configure all harm categories
        return [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=threshold
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=threshold
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=threshold
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=threshold
            ),
        ]

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        reference_images: Optional[List] = None,
        negative_prompt: Optional[str] = None,
        safety_threshold: str = "block_medium_and_above",
        allow_adult_imagery: bool = False,
        bypass_safety_filters: bool = False,
        **kwargs
    ) -> bytes:
        """
        Generate an image using Google Gemini 2.5 Flash Image.

        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Aspect ratio (e.g., "16:9", "3:4", "1:1")
            reference_images: List of reference image bytes for character consistency
            negative_prompt: Not used by Gemini (kept for interface compatibility)
            safety_threshold: Safety filter threshold
            allow_adult_imagery: Allow adult characters in images
            bypass_safety_filters: Completely disable safety filters
            **kwargs: Additional parameters

        Returns:
            PNG image data as bytes

        Raises:
            Exception: If image generation fails
        """
        try:
            # Use provided aspect ratio or default
            ratio = aspect_ratio or self.aspect_ratio

            # Enhance prompt for children's content (unless bypassing filters)
            if bypass_safety_filters:
                enhanced_prompt = prompt
                logger.warning("Safety filters bypassed - using raw prompt")
            else:
                enhanced_prompt = self._enhance_prompt_for_children(prompt)

            # Add character consistency instruction if reference images provided
            if reference_images:
                enhanced_prompt = f"""IMPORTANT: Use the reference image(s) provided to maintain EXACT character consistency. The characters' physical appearance, clothing, and distinctive features MUST match the reference exactly.

{enhanced_prompt}

CRITICAL: Ensure all characters look identical to their appearance in the reference image(s)."""

            logger.info(f"Generating image with Gemini model: {self.model}")
            logger.debug(f"Prompt: {enhanced_prompt[:200]}...")
            logger.debug(f"Aspect ratio: {ratio}")
            logger.debug(f"Safety threshold: {safety_threshold}")

            # Build contents (prompt + optional reference images)
            contents = []

            # Add reference images if provided (for character consistency)
            if reference_images:
                logger.info(f"Using {len(reference_images)} reference images for consistency")
                for ref_img in reference_images:
                    # Convert bytes to PIL Image for Gemini
                    pil_img = PILImage.open(BytesIO(ref_img))
                    contents.append(pil_img)

            # Add the text prompt
            contents.append(enhanced_prompt)

            # Generate image using Gemini API
            client = self._get_client()

            # Build safety settings
            safety_settings = self._build_safety_settings(
                safety_threshold=safety_threshold,
                bypass_safety_filters=bypass_safety_filters
            )

            # Configure generation
            config = GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=ImageConfig(
                    aspect_ratio=ratio
                ),
                safety_settings=safety_settings,
            )

            # Call Gemini API
            logger.debug(f"Calling generate_content with {len(contents)} content parts")
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=self.model,
                contents=contents,
                config=config,
            )

            # Extract image from response
            if not response.candidates:
                # Check if content was blocked
                if hasattr(response, 'prompt_feedback'):
                    feedback = response.prompt_feedback
                    logger.error(f"Gemini blocked the request. Feedback: {feedback}")
                    raise ValueError(f"Content blocked by Gemini safety filters: {feedback}")
                raise ValueError("No candidates returned from Gemini API")

            logger.debug(f"Received {len(response.candidates)} candidates")

            # Check if first candidate was blocked
            candidate = response.candidates[0]

            # Check if content is None (blocked by safety filters)
            if candidate.content is None:
                finish_reason = str(getattr(candidate, 'finish_reason', 'UNKNOWN'))
                safety_ratings = getattr(candidate, 'safety_ratings', 'N/A')
                logger.error(f"Content blocked. Finish reason: {finish_reason}")
                logger.error(f"Safety ratings: {safety_ratings}")
                raise ValueError(f"Image generation blocked by safety filters: {finish_reason}. Try adjusting safety settings or modifying the prompt.")

            if hasattr(candidate, 'finish_reason'):
                finish_reason = str(candidate.finish_reason)
                if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                    logger.error(f"Candidate blocked. Finish reason: {finish_reason}")
                    logger.error(f"Safety ratings: {getattr(candidate, 'safety_ratings', 'N/A')}")
                    raise ValueError(f"Image generation blocked due to safety: {finish_reason}")

            # Look for image in response parts
            for part in candidate.content.parts:
                logger.debug(f"Processing part: {type(part)}")

                # Check if this part contains an image
                if hasattr(part, 'as_image'):
                    logger.debug("Found image part, extracting...")

                    # Get SDK image wrapper
                    sdk_image = part.as_image()

                    # Extract PIL Image
                    pil_image = sdk_image._pil_image

                    # Normalize to exact aspect ratio
                    normalized_image = self._normalize_aspect_ratio(pil_image, ratio)

                    # Convert to PNG bytes
                    image_buffer = BytesIO()
                    normalized_image.save(image_buffer, format='PNG')
                    image_bytes = image_buffer.getvalue()

                    logger.info(f"Successfully generated image ({len(image_bytes)} bytes)")
                    return image_bytes

            # No image found in any part
            raise ValueError("No image data found in response parts")

        except Exception as e:
            logger.error(f"Failed to generate image with Gemini: {e}")
            raise

    def _normalize_aspect_ratio(self, image: PILImage.Image, target_ratio: str) -> PILImage.Image:
        """
        Normalize image to exact aspect ratio by center cropping.

        Args:
            image: PIL Image to normalize
            target_ratio: Target aspect ratio string (e.g., "16:9", "1:1", "3:4")

        Returns:
            Cropped PIL Image with exact aspect ratio
        """
        # Parse target aspect ratio
        try:
            w_ratio, h_ratio = map(int, target_ratio.split(':'))
            target_aspect = w_ratio / h_ratio
        except (ValueError, ZeroDivisionError):
            logger.warning(f"Invalid aspect ratio '{target_ratio}', returning original image")
            return image

        # Get current dimensions
        width, height = image.size
        current_aspect = width / height

        # Check if already correct (within 1% tolerance)
        if abs(current_aspect - target_aspect) / target_aspect < 0.01:
            logger.debug(f"Image already at target aspect ratio {target_ratio}")
            return image

        # Calculate crop dimensions
        if current_aspect > target_aspect:
            # Image is wider than target - crop sides
            new_width = int(height * target_aspect)
            new_height = height
            left = (width - new_width) // 2
            top = 0
        else:
            # Image is taller than target - crop top/bottom
            new_width = width
            new_height = int(width / target_aspect)
            left = 0
            top = (height - new_height) // 2

        # Crop to exact aspect ratio
        cropped = image.crop((left, top, left + new_width, top + new_height))
        logger.debug(f"Normalized image from {width}x{height} to {new_width}x{new_height} for ratio {target_ratio}")

        return cropped

    def _enhance_prompt_for_children(self, prompt: str) -> str:
        """
        Enhance prompt for children's content.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt for children's content
        """
        # Call base implementation
        base_enhanced = super()._enhance_prompt_for_children(prompt)

        # Add Gemini-specific instructions for better quality
        gemini_specific = (
            " Create a high-quality children's book illustration. "
            "Use vibrant, appealing colors and a warm, inviting composition. "
            "Ensure all elements are clearly visible and age-appropriate."
        )

        return f"{base_enhanced}{gemini_specific}"
