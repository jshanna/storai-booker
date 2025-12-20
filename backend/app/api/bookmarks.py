"""API routes for story bookmarks."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends
from beanie import PydanticObjectId
from loguru import logger

from app.models.bookmark import Bookmark
from app.models.storybook import Storybook
from app.models.user import User
from app.schemas.bookmark import (
    BookmarkResponse,
    BookmarkWithStoryResponse,
    BookmarkListResponse,
    BookmarkStatusResponse,
)
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("", response_model=BookmarkListResponse)
async def list_bookmarks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
):
    """
    List current user's bookmarked stories with pagination.

    Returns bookmarks with story details, sorted by bookmark creation time (newest first).
    Only returns bookmarks for stories that are still shared.
    """
    try:
        user_id = str(current_user.id)

        # Get total count of user's bookmarks
        total = await Bookmark.find({"user_id": user_id}).count()

        # Get paginated bookmarks (newest first)
        skip = (page - 1) * page_size
        bookmarks = await Bookmark.find({"user_id": user_id}).sort("-created_at").skip(skip).limit(page_size).to_list()

        # Build response with story details
        bookmark_items = []
        for bookmark in bookmarks:
            try:
                # Get the story
                story = await Storybook.get(PydanticObjectId(bookmark.story_id))
                if not story:
                    # Story was deleted, skip it
                    continue

                # Only include if story is still shared
                if not story.is_shared:
                    continue

                # Get owner name
                owner_name = None
                try:
                    owner = await User.get(PydanticObjectId(story.user_id))
                    if owner:
                        owner_name = owner.full_name or "Anonymous"
                except Exception:
                    pass

                bookmark_items.append(BookmarkWithStoryResponse(
                    id=str(bookmark.id),
                    story_id=bookmark.story_id,
                    story_title=story.title,
                    cover_image_url=story.cover_image_url,
                    format=story.generation_inputs.format,
                    page_count=story.generation_inputs.page_count,
                    owner_name=owner_name,
                    share_token=story.share_token,
                    created_at=bookmark.created_at,
                    story_created_at=story.created_at,
                ))
            except Exception as e:
                logger.warning(f"Error fetching story for bookmark {bookmark.id}: {e}")
                continue

        return BookmarkListResponse(
            bookmarks=bookmark_items,
            total=len(bookmark_items),  # Actual count after filtering
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list bookmarks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list bookmarks: {str(e)}",
        )


@router.post("/{story_id}", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    story_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Bookmark a shared story.

    The story must exist and have sharing enabled.
    Returns 409 if already bookmarked.
    """
    try:
        user_id = str(current_user.id)

        # Validate story ID format
        try:
            story_obj_id = PydanticObjectId(story_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid story ID format",
            )

        # Check story exists and is shared
        story = await Storybook.get(story_obj_id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found",
            )
        if not story.is_shared:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot bookmark a story that is not shared",
            )

        # Check if already bookmarked
        existing = await Bookmark.find_one({"user_id": user_id, "story_id": story_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Story is already bookmarked",
            )

        # Create bookmark
        bookmark = Bookmark(user_id=user_id, story_id=story_id)
        await bookmark.insert()

        logger.info(f"User {user_id} bookmarked story {story_id}")

        return BookmarkResponse(
            id=str(bookmark.id),
            story_id=bookmark.story_id,
            created_at=bookmark.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add bookmark: {str(e)}",
        )


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    story_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove a bookmark.

    Only the bookmark owner can remove it.
    """
    try:
        user_id = str(current_user.id)

        # Find and delete the bookmark
        bookmark = await Bookmark.find_one({"user_id": user_id, "story_id": story_id})
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found",
            )

        await bookmark.delete()
        logger.info(f"User {user_id} removed bookmark for story {story_id}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove bookmark: {str(e)}",
        )


@router.get("/{story_id}/status", response_model=BookmarkStatusResponse)
async def get_bookmark_status(
    story_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Check if a story is bookmarked by the current user.
    """
    try:
        user_id = str(current_user.id)

        bookmark = await Bookmark.find_one({"user_id": user_id, "story_id": story_id})

        return BookmarkStatusResponse(
            is_bookmarked=bookmark is not None,
            bookmark_id=str(bookmark.id) if bookmark else None,
        )
    except Exception as e:
        logger.error(f"Failed to get bookmark status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bookmark status: {str(e)}",
        )
