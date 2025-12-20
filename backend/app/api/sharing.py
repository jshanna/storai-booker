"""API routes for story sharing and comments."""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends, Request
from beanie import PydanticObjectId
from loguru import logger

from app.models.storybook import Storybook
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreateRequest, CommentResponse, CommentListResponse
from app.schemas.share import ShareResponse, SharedStoryResponse, PublicStoryListItem, PublicStoriesListResponse
from app.schemas.story import PageResponse
from app.services.sanitizer import sanitizer
from app.api.dependencies import get_current_active_user, get_optional_user

router = APIRouter()


def get_share_url(request: Request, token: str) -> str:
    """Generate the full share URL for a token."""
    # Get base URL from request
    base_url = str(request.base_url).rstrip("/")
    # Replace /api with frontend URL pattern
    if "/api" in base_url:
        base_url = base_url.replace("/api", "")
    return f"{base_url}/shared/{token}"


@router.get("/shared", response_model=PublicStoriesListResponse)
async def list_public_stories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=50, description="Items per page"),
    format: Optional[str] = Query(None, pattern="^(storybook|comic)$", description="Filter by format"),
):
    """
    List all publicly shared stories with pagination.

    This is a public endpoint - no authentication required.
    Only returns completed stories that have sharing enabled.
    """
    try:
        # Build query for shared, completed stories
        query = {"is_shared": True, "status": "complete"}
        if format:
            query["generation_inputs.format"] = format

        # Get total count
        total = await Storybook.find(query).count()

        # Get paginated results (newest shared first)
        skip = (page - 1) * page_size
        stories = await Storybook.find(query).sort("-shared_at").skip(skip).limit(page_size).to_list()

        # Build response with owner names
        story_items = []
        for story in stories:
            # Try to get owner name
            owner_name = None
            try:
                owner = await User.get(PydanticObjectId(story.user_id))
                if owner:
                    owner_name = owner.full_name or "Anonymous"
            except Exception:
                pass

            story_items.append(PublicStoryListItem(
                id=str(story.id),
                title=story.title,
                cover_image_url=story.cover_image_url,
                format=story.generation_inputs.format,
                page_count=story.generation_inputs.page_count,
                owner_name=owner_name,
                share_token=story.share_token,
                shared_at=story.shared_at,
                created_at=story.created_at,
            ))

        return PublicStoriesListResponse(
            stories=story_items,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list public stories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list public stories: {str(e)}",
        )


@router.post("/stories/{story_id}/share", response_model=ShareResponse)
async def enable_sharing(
    story_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Enable sharing for a story.

    Generates a unique share token and marks the story as shared.
    Only the story owner can enable sharing.
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
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )
        if story.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to share this story",
            )

        # Generate share token if not already shared
        if not story.share_token:
            story.share_token = secrets.token_urlsafe(24)

        story.is_shared = True
        story.shared_at = datetime.now(timezone.utc)
        story.updated_at = datetime.now(timezone.utc)
        await story.save()

        logger.info(f"Enabled sharing for story {story_id} by user {user_id}")

        return ShareResponse(
            story_id=str(story.id),
            is_shared=True,
            share_token=story.share_token,
            share_url=get_share_url(request, story.share_token),
            shared_at=story.shared_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable sharing for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable sharing: {str(e)}",
        )


@router.delete("/stories/{story_id}/share", response_model=ShareResponse)
async def disable_sharing(
    story_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Disable sharing for a story.

    Clears the share token and marks the story as not shared.
    Existing comments are preserved but will be inaccessible.
    Only the story owner can disable sharing.
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
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story {story_id} not found",
            )
        if story.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify sharing for this story",
            )

        story.is_shared = False
        story.share_token = None
        story.shared_at = None
        story.updated_at = datetime.now(timezone.utc)
        await story.save()

        logger.info(f"Disabled sharing for story {story_id} by user {user_id}")

        return ShareResponse(
            story_id=str(story.id),
            is_shared=False,
            share_token=None,
            share_url=None,
            shared_at=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable sharing for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable sharing: {str(e)}",
        )


@router.get("/shared/{token}", response_model=SharedStoryResponse)
async def get_shared_story(
    token: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Get a shared story by its share token.

    This is a public endpoint - no authentication required.
    Returns the story content for anyone with the share link.
    """
    try:
        # Find story by share token
        story = await Storybook.find_one({"share_token": token, "is_shared": True})
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared story not found or sharing has been disabled",
            )

        # Get owner info for display (optional)
        owner_name = None
        try:
            owner = await User.get(PydanticObjectId(story.user_id))
            if owner:
                owner_name = owner.full_name or "Anonymous"
        except Exception:
            pass

        return SharedStoryResponse(
            id=str(story.id),
            title=story.title,
            created_at=story.created_at,
            updated_at=story.updated_at,
            generation_inputs=story.generation_inputs,
            metadata=story.metadata,
            pages=[PageResponse(**page.model_dump()) for page in story.pages],
            status=story.status,
            cover_image_url=story.cover_image_url,
            is_shared=True,
            shared_at=story.shared_at,
            owner_name=owner_name,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get shared story with token {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get shared story: {str(e)}",
        )


@router.get("/shared/{token}/comments", response_model=CommentListResponse)
async def list_comments(
    token: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    List comments on a shared story.

    This is a public endpoint - no authentication required.
    Comments are sorted by creation time (newest first).
    """
    try:
        # Verify story exists and is shared
        story = await Storybook.find_one({"share_token": token, "is_shared": True})
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared story not found or sharing has been disabled",
            )

        story_id = str(story.id)

        # Get total count
        total = await Comment.find({"story_id": story_id}).count()

        # Get paginated comments (newest first)
        skip = (page - 1) * page_size
        comments = await Comment.find({"story_id": story_id}).sort("-created_at").skip(skip).limit(page_size).to_list()

        return CommentListResponse(
            comments=[
                CommentResponse(
                    id=str(comment.id),
                    story_id=comment.story_id,
                    user_id=comment.user_id,
                    author_name=comment.author_name,
                    author_avatar_url=comment.author_avatar_url,
                    text=comment.text,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                    is_edited=comment.is_edited,
                )
                for comment in comments
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list comments for shared story {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list comments: {str(e)}",
        )


@router.post("/shared/{token}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    token: str,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Add a comment to a shared story.

    Requires authentication. Rate limited to 10 comments per minute per user.
    """
    try:
        user_id = str(current_user.id)

        # Verify story exists and is shared
        story = await Storybook.find_one({"share_token": token, "is_shared": True})
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared story not found or sharing has been disabled",
            )

        story_id = str(story.id)

        # Simple rate limiting: check last 10 comments in 1 minute
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        recent_comments = await Comment.find({
            "user_id": user_id,
            "created_at": {"$gte": one_minute_ago}
        }).count()

        if recent_comments >= 10:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait before posting more comments.",
            )

        # Sanitize comment text
        try:
            sanitized_text = sanitizer.sanitize_text(request.text)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # Create comment
        comment = Comment(
            story_id=story_id,
            user_id=user_id,
            author_name=current_user.full_name or "Anonymous",
            author_avatar_url=current_user.avatar_url,
            text=sanitized_text,
        )
        await comment.insert()

        logger.info(f"Created comment {comment.id} on story {story_id} by user {user_id}")

        return CommentResponse(
            id=str(comment.id),
            story_id=comment.story_id,
            user_id=comment.user_id,
            author_name=comment.author_name,
            author_avatar_url=comment.author_avatar_url,
            text=comment.text,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_edited=comment.is_edited,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create comment on shared story {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}",
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a comment.

    Requires authentication. Only the comment author or story owner can delete.
    """
    try:
        user_id = str(current_user.id)

        # Validate ObjectId
        try:
            obj_id = PydanticObjectId(comment_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid comment ID format",
            )

        # Find comment
        comment = await Comment.get(obj_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment {comment_id} not found",
            )

        # Check authorization: comment author or story owner
        can_delete = comment.user_id == user_id

        if not can_delete:
            # Check if user is story owner
            story = await Storybook.find_one({"_id": PydanticObjectId(comment.story_id)})
            if story and story.user_id == user_id:
                can_delete = True

        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this comment",
            )

        await comment.delete()
        logger.info(f"Deleted comment {comment_id} by user {user_id}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}",
        )
