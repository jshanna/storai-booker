"""Image composition service for creating covers with title overlays."""

import io
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from loguru import logger


class ImageCompositor:
    """Service for compositing images, primarily for creating cover images with title overlays."""

    def __init__(self, font_path: Optional[str] = None):
        """
        Initialize image compositor.

        Args:
            font_path: Optional path to custom TTF/OTF font file
        """
        self.font_path = font_path

    async def create_cover_with_title(
        self,
        image_bytes: bytes,
        title: str,
        title_color: Tuple[int, int, int] = (255, 255, 255),  # White
        shadow_color: Tuple[int, int, int] = (0, 0, 0),  # Black
        background_alpha: int = 128,  # Semi-transparent
    ) -> bytes:
        """
        Create a cover image with title overlay.

        Adds a semi-transparent gradient background at the bottom of the image
        and overlays the title text with a shadow for readability.

        Args:
            image_bytes: Input image as PNG bytes
            title: Title text to overlay
            title_color: RGB color for title text
            shadow_color: RGB color for text shadow
            background_alpha: Alpha value for background overlay (0-255)

        Returns:
            Composited image as PNG bytes

        Raises:
            Exception: If image processing fails
        """
        try:
            logger.info(f"Creating cover with title: '{title}'")

            # Load image and convert to RGBA for transparency support
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            width, height = img.size
            logger.debug(f"Image size: {width}x{height}")

            # Create overlay for text background
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Add gradient background at bottom third
            self._add_text_background(draw, img.size, background_alpha)

            # Composite the overlay onto the image
            img = Image.alpha_composite(img, overlay)

            # Now draw the title text
            draw = ImageDraw.Draw(img)
            self._draw_title(
                draw,
                title,
                img.size,
                title_color=title_color,
                shadow_color=shadow_color,
            )

            # Convert to RGB for PNG output (remove alpha channel)
            final_img = img.convert('RGB')

            # Save to bytes
            output = io.BytesIO()
            final_img.save(output, format='PNG', quality=95, optimize=True)
            output_bytes = output.getvalue()

            logger.info(f"Cover created successfully ({len(output_bytes)} bytes)")
            return output_bytes

        except Exception as e:
            logger.error(f"Failed to create cover with title: {e}")
            raise

    def _add_text_background(
        self,
        draw: ImageDraw.ImageDraw,
        size: Tuple[int, int],
        alpha: int,
    ) -> None:
        """
        Add a gradient background for text readability.

        Creates a semi-transparent gradient from transparent at top to solid
        at the bottom third of the image.

        Args:
            draw: PIL ImageDraw object
            size: Image size (width, height)
            alpha: Maximum alpha value for the gradient
        """
        width, height = size

        # Background covers bottom 35% of image
        bg_height = int(height * 0.35)
        bg_top = height - bg_height

        # Create gradient from transparent to semi-transparent
        for i in range(bg_height):
            # Gradient from 0 to alpha
            current_alpha = int((i / bg_height) * alpha)
            y = bg_top + i

            draw.rectangle(
                [(0, y), (width, y + 1)],
                fill=(0, 0, 0, current_alpha)
            )

    def _draw_title(
        self,
        draw: ImageDraw.ImageDraw,
        title: str,
        size: Tuple[int, int],
        title_color: Tuple[int, int, int],
        shadow_color: Tuple[int, int, int],
    ) -> None:
        """
        Draw title text with shadow.

        Args:
            draw: PIL ImageDraw object
            title: Title text
            size: Image size (width, height)
            title_color: RGB color for title
            shadow_color: RGB color for shadow
        """
        width, height = size

        # Load font
        font = self._get_font(size)

        # Calculate text size and position
        # For PIL 10.x, use textbbox instead of textsize
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center horizontally, position in bottom third
        x = (width - text_width) // 2
        y = height - int(height * 0.20) - text_height // 2

        # Draw shadow (offset by a few pixels)
        shadow_offset = max(2, int(height * 0.003))  # Scale with image size
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            title,
            font=font,
            fill=shadow_color + (200,),  # Add alpha to shadow
        )

        # Draw title text
        draw.text(
            (x, y),
            title,
            font=font,
            fill=title_color + (255,),  # Fully opaque
        )

    def _get_font(self, size: Tuple[int, int]) -> ImageFont.FreeTypeFont:
        """
        Get font for title text.

        Tries to use custom font if provided, otherwise falls back to
        default system fonts.

        Args:
            size: Image size (width, height) for scaling font size

        Returns:
            PIL FreeTypeFont object
        """
        width, height = size

        # Calculate font size based on image dimensions
        # Use about 6% of image height for font size
        font_size = int(height * 0.06)

        # Try custom font first
        if self.font_path:
            try:
                return ImageFont.truetype(self.font_path, font_size)
            except Exception as e:
                logger.warning(f"Failed to load custom font {self.font_path}: {e}")

        # Try common system fonts
        system_fonts = [
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
            # Windows
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]

        for font_path in system_fonts:
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                continue

        # Fallback to default font
        logger.warning("Using default PIL font (not ideal for titles)")
        return ImageFont.load_default()
