"""API routes for application settings management."""
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.models.settings import AppSettings
from app.schemas.settings import SettingsUpdateRequest, SettingsResponse

router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """
    Get application settings.

    Returns the settings for the default user. In Phase 6 (multi-user),
    this will be scoped to the authenticated user.
    """
    try:
        # Get or create default settings
        settings = await AppSettings.find_one({"user_id": "default"})

        if not settings:
            # Create default settings if they don't exist
            settings = AppSettings(user_id="default")
            await settings.insert()
            logger.info("Created default application settings")

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
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}",
        )


@router.put("", response_model=SettingsResponse)
async def update_settings(request: SettingsUpdateRequest):
    """
    Update application settings.

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    try:
        # Get or create settings
        settings = await AppSettings.find_one({"user_id": "default"})

        if not settings:
            settings = AppSettings(user_id="default")
            await settings.insert()
            logger.info("Created default application settings")

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(settings, field, value)

        await settings.save()
        logger.info("Updated application settings")

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
async def reset_settings():
    """
    Reset settings to defaults.

    Deletes current settings and creates fresh defaults.
    """
    try:
        # Delete existing settings
        settings = await AppSettings.find_one({"user_id": "default"})
        if settings:
            await settings.delete()
            logger.info("Deleted existing settings")

        # Create new default settings
        settings = AppSettings(user_id="default")
        await settings.insert()
        logger.info("Reset settings to defaults")

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
