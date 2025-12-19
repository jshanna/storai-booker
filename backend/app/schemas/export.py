"""Pydantic schemas for export API."""

from enum import Enum
from pydantic import BaseModel, ConfigDict


class ExportFormat(str, Enum):
    """Available export formats."""

    PDF = "pdf"
    IMAGES = "images"
    CBZ = "cbz"
    EPUB = "epub"


class ExportRequest(BaseModel):
    """Export request schema."""

    format: ExportFormat

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "format": "pdf",
            }
        }
    )


class ExportResponse(BaseModel):
    """Export response schema with download info."""

    story_id: str
    format: str
    filename: str
    size: int
    content_type: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story_id": "507f1f77bcf86cd799439011",
                "format": "pdf",
                "filename": "My_Story.pdf",
                "size": 1024000,
                "content_type": "application/pdf",
            }
        }
    )
