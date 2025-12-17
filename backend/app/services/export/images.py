"""Images ZIP export service."""

import io
import zipfile
from loguru import logger

from .base import BaseExporter, ExportResult


class ImagesExporter(BaseExporter):
    """Export storybook images as ZIP archive."""

    async def export(self, story) -> ExportResult:
        """
        Export story images to ZIP.

        Args:
            story: Storybook document

        Returns:
            ExportResult with ZIP data
        """
        logger.info(f"Exporting story '{story.title}' images to ZIP")

        # Create ZIP buffer
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add cover image
            if story.cover_image_url:
                cover_data = await self.download_image(story.cover_image_url)
                if cover_data:
                    zf.writestr("00_cover.png", cover_data)

            # Add page images
            for page in story.pages:
                if page.illustration_url:
                    img_data = await self.download_image(page.illustration_url)
                    if img_data:
                        filename = f"{page.page_number:02d}_page_{page.page_number}.png"
                        zf.writestr(filename, img_data)

            # Add metadata file
            metadata = self._create_metadata(story)
            zf.writestr("metadata.txt", metadata)

        # Get ZIP data
        zip_data = buffer.getvalue()
        buffer.close()

        filename = f"{self.sanitize_filename(story.title)}_images.zip"

        logger.info(f"ZIP export complete: {filename} ({len(zip_data)} bytes)")

        return ExportResult(
            data=zip_data,
            filename=filename,
            content_type="application/zip",
            size=len(zip_data),
        )

    def _create_metadata(self, story) -> str:
        """
        Create metadata text file content.

        Args:
            story: Storybook document

        Returns:
            Metadata string
        """
        lines = [
            f"Title: {story.title}",
            f"Format: {story.generation_inputs.format}",
            f"Target Age: {story.generation_inputs.audience_age}",
            f"Pages: {len(story.pages)}",
            f"Topic: {story.generation_inputs.topic}",
            f"Setting: {story.generation_inputs.setting}",
            f"Style: {story.generation_inputs.illustration_style}",
            "",
            "Page Text:",
            "-" * 40,
        ]

        for page in story.pages:
            lines.append(f"\nPage {page.page_number}:")
            lines.append(page.text or "(No text)")

        return "\n".join(lines)
