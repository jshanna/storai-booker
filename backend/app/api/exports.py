"""API routes for story export functionality."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from beanie import PydanticObjectId
from loguru import logger
import io

from app.models.storybook import Storybook
from app.models.user import User
from app.schemas.export import ExportFormat, ExportResponse
from app.services.export import PDFExporter, ImagesExporter, ComicExporter, EPUBExporter
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/{story_id}/{format}", response_class=StreamingResponse)
async def export_story(
    story_id: str,
    format: ExportFormat,
    current_user: User = Depends(get_current_active_user),
):
    """
    Export a story to the specified format.

    Downloads the exported file directly.

    Supported formats:
    - pdf: PDF document with text and images
    - images: ZIP archive of all images
    - cbz: Comic book archive (for comic format stories)
    - epub: EPUB e-book format

    Requires authentication. Only exports stories owned by the current user.
    """
    try:
        user_id = str(current_user.id)

        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Find story and verify ownership
        story = await Storybook.get(obj_id)
        if not story or story.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )

        # Check story status
        if story.status != "complete":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot export story with status '{story.status}'. Story must be complete.",
            )

        # Select exporter based on format
        if format == ExportFormat.PDF:
            exporter = PDFExporter()
        elif format == ExportFormat.IMAGES:
            exporter = ImagesExporter()
        elif format == ExportFormat.CBZ:
            exporter = ComicExporter(format="cbz")
        elif format == ExportFormat.EPUB:
            exporter = EPUBExporter()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}",
            )

        logger.info(f"Exporting story {story_id} to {format} for user {user_id}")

        # Export the story
        result = await exporter.export(story)

        # Stream the response
        return StreamingResponse(
            io.BytesIO(result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "Content-Length": str(result.size),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export story: {str(e)}",
        )


@router.get("/{story_id}/{format}/info", response_model=ExportResponse)
async def get_export_info(
    story_id: str,
    format: ExportFormat,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get export information without downloading.

    Returns metadata about the export (filename, size, etc.)
    This is useful for showing export options in the UI.

    Requires authentication. Only returns info for stories owned by the current user.
    """
    try:
        user_id = str(current_user.id)

        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Find story and verify ownership
        story = await Storybook.get(obj_id)
        if not story or story.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )

        # Check story status
        if story.status != "complete":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot export story with status '{story.status}'. Story must be complete.",
            )

        # Select exporter based on format
        if format == ExportFormat.PDF:
            exporter = PDFExporter()
        elif format == ExportFormat.IMAGES:
            exporter = ImagesExporter()
        elif format == ExportFormat.CBZ:
            exporter = ComicExporter(format="cbz")
        elif format == ExportFormat.EPUB:
            exporter = EPUBExporter()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}",
            )

        # Export to get size info
        result = await exporter.export(story)

        return ExportResponse(
            story_id=story_id,
            format=format.value,
            filename=result.filename,
            size=result.size,
            content_type=result.content_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get export info for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export info: {str(e)}",
        )
