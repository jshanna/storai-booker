"""Base exporter class and common utilities."""

import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx
from loguru import logger


@dataclass
class ExportResult:
    """Result of an export operation."""

    data: bytes
    filename: str
    content_type: str
    size: int


class BaseExporter(ABC):
    """Base class for all exporters."""

    @abstractmethod
    async def export(self, story) -> ExportResult:
        """
        Export a story to the target format.

        Args:
            story: Storybook document to export

        Returns:
            ExportResult with the exported data
        """
        pass

    async def download_image(self, url: str) -> Optional[bytes]:
        """
        Download image from URL.

        Args:
            url: URL to download from

        Returns:
            Image bytes or None if download fails
        """
        if not url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return None

    def sanitize_filename(self, title: str, max_length: int = 50) -> str:
        """
        Sanitize title for use as filename.

        Args:
            title: Title to sanitize
            max_length: Maximum filename length

        Returns:
            Sanitized filename
        """
        # Replace unsafe characters
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        # Remove multiple spaces/underscores
        while "  " in safe:
            safe = safe.replace("  ", " ")
        while "__" in safe:
            safe = safe.replace("__", "_")
        # Trim and limit length
        safe = safe.strip().strip("_")[:max_length]
        return safe or "story"
