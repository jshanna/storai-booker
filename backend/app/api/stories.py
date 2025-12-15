"""API routes for story management."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from beanie import PydanticObjectId
from loguru import logger

from app.models.storybook import Storybook
from app.schemas.story import (
    StoryCreateRequest,
    StoryResponse,
    StoryListResponse,
    StoryStatusResponse,
    PageResponse,
)

router = APIRouter()


@router.post("/generate", response_model=StoryResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_story(request: StoryCreateRequest):
    """
    Initiate story generation.

    This endpoint creates a new story document and queues it for generation.
    The actual generation happens asynchronously via Celery workers (Phase 2).
    """
    try:
        # Create new storybook document
        storybook = Storybook(
            title=request.title,
            generation_inputs=request.generation_inputs,
            status="pending",
        )

        await storybook.insert()
        logger.info(f"Created story {storybook.id} - {storybook.title}")

        # TODO: Phase 2 - Queue generation job with Celery
        # celery_app.send_task('app.tasks.generate_story', args=[str(storybook.id)])

        return StoryResponse(
            id=str(storybook.id),
            title=storybook.title,
            created_at=storybook.created_at,
            updated_at=storybook.updated_at,
            generation_inputs=storybook.generation_inputs,
            metadata=storybook.metadata,
            pages=[PageResponse(**page.model_dump()) for page in storybook.pages],
            status=storybook.status,
            error_message=storybook.error_message,
            cover_image_url=storybook.cover_image_url,
        )
    except Exception as e:
        logger.error(f"Failed to create story: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create story: {str(e)}",
        )


@router.get("", response_model=StoryListResponse)
async def list_stories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    format: Optional[str] = Query(None, pattern="^(storybook|comic)$", description="Filter by format"),
    status: Optional[str] = Query(None, pattern="^(pending|generating|complete|error)$", description="Filter by status"),
    search: Optional[str] = Query(None, min_length=1, description="Search in title"),
):
    """
    List stories with pagination and filtering.

    Supports:
    - Pagination via page and page_size
    - Filtering by format (storybook/comic) and status
    - Text search in title
    """
    try:
        # Build query filters
        query = {}
        if format:
            query["generation_inputs.format"] = format
        if status:
            query["status"] = status
        if search:
            # MongoDB text search
            query["$text"] = {"$search": search}

        # Get total count
        total = await Storybook.find(query).count()

        # Get paginated results
        skip = (page - 1) * page_size
        stories = await Storybook.find(query).sort("-created_at").skip(skip).limit(page_size).to_list()

        return StoryListResponse(
            stories=[
                StoryResponse(
                    id=str(story.id),
                    title=story.title,
                    created_at=story.created_at,
                    updated_at=story.updated_at,
                    generation_inputs=story.generation_inputs,
                    metadata=story.metadata,
                    pages=[PageResponse(**page.model_dump()) for page in story.pages],
                    status=story.status,
                    error_message=story.error_message,
                    cover_image_url=story.cover_image_url,
                )
                for story in stories
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list stories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list stories: {str(e)}",
        )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """
    Get a specific story by ID.
    """
    try:
        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Find story
        story = await Storybook.get(obj_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )

        return StoryResponse(
            id=str(story.id),
            title=story.title,
            created_at=story.created_at,
            updated_at=story.updated_at,
            generation_inputs=story.generation_inputs,
            metadata=story.metadata,
            pages=[PageResponse(**page.model_dump()) for page in story.pages],
            status=story.status,
            error_message=story.error_message,
            cover_image_url=story.cover_image_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get story: {str(e)}",
        )


@router.get("/{story_id}/status", response_model=StoryStatusResponse)
async def get_story_status(story_id: str):
    """
    Get story generation status.

    Useful for polling progress during generation.
    """
    try:
        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Find story
        story = await Storybook.get(obj_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )

        # Calculate progress if generating
        progress = None
        current_step = None
        if story.status == "generating":
            total_pages = story.generation_inputs.page_count
            completed_pages = len([p for p in story.pages if p.validated])
            progress = completed_pages / total_pages if total_pages > 0 else 0.0
            current_step = f"Generating page {completed_pages + 1}/{total_pages}"

        return StoryStatusResponse(
            id=str(story.id),
            status=story.status,
            progress=progress,
            current_step=current_step,
            error_message=story.error_message,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get story status {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get story status: {str(e)}",
        )


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(story_id: str):
    """
    Delete a story by ID.

    This also deletes associated image files from storage (Phase 1 - storage service).
    """
    try:
        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Find and delete story
        story = await Storybook.get(obj_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )

        # Delete associated files from storage
        from app.services.storage import storage_service
        try:
            await storage_service.delete_story_files(str(story_id))
        except Exception as e:
            logger.warning(f"Failed to delete files for story {story_id}: {e}")

        await story.delete()
        logger.info(f"Deleted story {story_id}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete story: {str(e)}",
        )
