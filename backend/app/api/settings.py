"""API routes for application settings management."""
from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger

from app.models.settings import AppSettings
from app.models.user import User
from app.schemas.settings import SettingsUpdateRequest, SettingsResponse
from app.services.cache import cache_service
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get application settings for the current user.

    Requires authentication. Returns user-specific settings.
    """
    try:
        user_id = str(current_user.id)

        # Build cache key (user-specific)
        cache_key = f"settings:{user_id}"

        # Try to get from cache
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for settings: {user_id}")
            return SettingsResponse(**cached)

        # Get or create user settings
        settings = await AppSettings.find_one({"user_id": user_id})

        if not settings:
            # Create default settings for this user
            settings = AppSettings(user_id=user_id)
            await settings.insert()
            logger.info(f"Created default settings for user {user_id}")

        response = SettingsResponse(
            id=str(settings.id),
            user_id=settings.user_id,
            age_range=settings.age_range,
            content_filters=settings.content_filters,
            generation_limits=settings.generation_limits,
            primary_llm_provider=settings.primary_llm_provider,
            fallback_llm_provider=settings.fallback_llm_provider,
            defaults=settings.defaults,
        )

        # Cache the response (TTL: 10 minutes for settings)
        cache_service.set(cache_key, response.model_dump(), ttl=600)

        return response
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}",
        )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    request: SettingsUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update application settings for the current user.

    Only provided fields will be updated. Omitted fields remain unchanged.
    Requires authentication.
    """
    try:
        user_id = str(current_user.id)

        # Get or create settings
        settings = await AppSettings.find_one({"user_id": user_id})

        if not settings:
            settings = AppSettings(user_id=user_id)
            await settings.insert()
            logger.info(f"Created default settings for user {user_id}")

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(settings, field, value)

        await settings.save()
        logger.info(f"Updated settings for user {user_id}")

        # Invalidate cache
        cache_service.delete(f"settings:{user_id}")

        return SettingsResponse(
            id=str(settings.id),
            user_id=settings.user_id,
            age_range=settings.age_range,
            content_filters=settings.content_filters,
            generation_limits=settings.generation_limits,
            primary_llm_provider=settings.primary_llm_provider,
            fallback_llm_provider=settings.fallback_llm_provider,
            defaults=settings.defaults,
        )
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}",
        )


@router.post("/reset", response_model=SettingsResponse)
async def reset_settings(
    current_user: User = Depends(get_current_active_user),
):
    """
    Reset settings to defaults for the current user.

    Deletes current settings and creates fresh defaults.
    Requires authentication.
    """
    try:
        user_id = str(current_user.id)

        # Delete existing settings
        settings = await AppSettings.find_one({"user_id": user_id})
        if settings:
            await settings.delete()
            logger.info(f"Deleted existing settings for user {user_id}")

        # Create new default settings
        settings = AppSettings(user_id=user_id)
        await settings.insert()
        logger.info(f"Reset settings to defaults for user {user_id}")

        # Invalidate cache
        cache_service.delete(f"settings:{user_id}")

        return SettingsResponse(
            id=str(settings.id),
            user_id=settings.user_id,
            age_range=settings.age_range,
            content_filters=settings.content_filters,
            generation_limits=settings.generation_limits,
            primary_llm_provider=settings.primary_llm_provider,
            fallback_llm_provider=settings.fallback_llm_provider,
            defaults=settings.defaults,
        )
    except Exception as e:
        logger.error(f"Failed to reset settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset settings: {str(e)}",
        )
