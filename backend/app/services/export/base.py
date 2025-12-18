"""Base exporter class and common utilities."""

import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx
from loguru import logger

from app.core.config import settings


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

    def _convert_to_internal_url(self, url: str) -> str:
        """
        Convert external URL to internal Docker URL for downloading.

        Handles multiple URL formats:
        - /storage/bucket/key -> http://minio:9000/bucket/key (public URL path)
        - http://localhost:9000/... -> http://minio:9000/... (external endpoint)
        """
        if not url:
            return url

        # Handle /storage/ public URL path (used in containerized setup)
        if url.startswith("/storage/"):
            internal_endpoint = settings.s3_endpoint_url or "http://minio:9000"
            return url.replace("/storage/", f"{internal_endpoint}/", 1)

        # Handle S3_PUBLIC_URL prefix if set (e.g., "http://localhost:3000/storage")
        if settings.s3_public_url and url.startswith(settings.s3_public_url):
            internal_endpoint = settings.s3_endpoint_url or "http://minio:9000"
            return url.replace(settings.s3_public_url, internal_endpoint, 1)

        # Convert external endpoint to internal endpoint
        external_endpoint = settings.s3_external_endpoint_url
        internal_endpoint = settings.s3_endpoint_url

        if external_endpoint and internal_endpoint and external_endpoint in url:
            return url.replace(external_endpoint, internal_endpoint)

        return url

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

        # Convert external URL to internal Docker URL
        internal_url = self._convert_to_internal_url(url)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(internal_url, timeout=30.0)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.warning(f"Failed to download image from {internal_url} (original: {url}): {e}")
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
