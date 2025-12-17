"""Comic book archive export service (CBZ/CBR)."""

import io
import zipfile
from loguru import logger

from .base import BaseExporter, ExportResult


class ComicExporter(BaseExporter):
    """
    Export storybooks as comic book archives.

    CBZ is a ZIP archive of images with .cbz extension.
    CBR would be RAR format but we use CBZ for simplicity.
    """

    def __init__(self, format: str = "cbz"):
        """
        Initialize comic exporter.

        Args:
            format: Export format ("cbz" or "cbr" - both produce ZIP)
        """
        self.format = format.lower()

    async def export(self, story) -> ExportResult:
        """
        Export story as comic book archive.

        Args:
            story: Storybook document

        Returns:
            ExportResult with CBZ data
        """
        logger.info(f"Exporting story '{story.title}' to {self.format.upper()}")

        # Create ZIP buffer
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add cover image as first page
            if story.cover_image_url:
                cover_data = await self.download_image(story.cover_image_url)
                if cover_data:
                    zf.writestr("000_cover.jpg", cover_data)

            # Add page images
            for page in story.pages:
                if page.illustration_url:
                    img_data = await self.download_image(page.illustration_url)
                    if img_data:
                        # Comic readers typically sort by filename
                        filename = f"{page.page_number:03d}.jpg"
                        zf.writestr(filename, img_data)

            # Add ComicInfo.xml for metadata
            comic_info = self._create_comic_info(story)
            zf.writestr("ComicInfo.xml", comic_info)

        # Get archive data
        archive_data = buffer.getvalue()
        buffer.close()

        filename = f"{self.sanitize_filename(story.title)}.{self.format}"
        content_type = "application/vnd.comicbook+zip" if self.format == "cbz" else "application/x-cbr"

        logger.info(f"{self.format.upper()} export complete: {filename} ({len(archive_data)} bytes)")

        return ExportResult(
            data=archive_data,
            filename=filename,
            content_type=content_type,
            size=len(archive_data),
        )

    def _create_comic_info(self, story) -> str:
        """
        Create ComicInfo.xml for comic book metadata.

        This is a standard format recognized by comic readers.

        Args:
            story: Storybook document

        Returns:
            ComicInfo XML string
        """
        # Escape XML special characters
        def escape(text: str) -> str:
            if not text:
                return ""
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        # Get character names
        characters = ", ".join(
            char.name for char in story.metadata.character_descriptions
        ) if story.metadata.character_descriptions else ""

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <Title>{escape(story.title)}</Title>
    <Summary>{escape(story.generation_inputs.topic)}</Summary>
    <Notes>{escape(story.generation_inputs.setting)}</Notes>
    <PageCount>{len(story.pages)}</PageCount>
    <Characters>{escape(characters)}</Characters>
    <Genre>Children</Genre>
    <AgeRating>{story.generation_inputs.audience_age}+</AgeRating>
    <Manga>No</Manga>
    <BlackAndWhite>No</BlackAndWhite>
</ComicInfo>"""

        return xml
