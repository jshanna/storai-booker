"""Story generation Celery tasks."""
import asyncio
from typing import Optional, List
from celery import group, chord
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.services.celery_app import celery_app
from app.core.config import settings
from app.models.storybook import Storybook, Page, StoryMetadata
from app.models.settings import AppSettings
from app.services.llm.provider_factory import LLMProviderFactory
from app.services.agents.coordinator import CoordinatorAgent
from app.services.agents.page_generator import PageGeneratorAgent
from app.services.agents.validator import ValidatorAgent
from app.services.image.provider_factory import ImageProviderFactory
from app.services.image.base import BaseImageProvider
from app.services.storage import storage_service
import httpx


# MongoDB connection management for Celery workers
_mongodb_client: Optional[AsyncIOMotorClient] = None


async def get_mongodb_client() -> AsyncIOMotorClient:
    """
    Get or create MongoDB client for Celery worker.

    Returns:
        MongoDB client instance
    """
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        # Initialize Beanie
        await init_beanie(
            database=_mongodb_client[settings.mongodb_db_name],
            document_models=[Storybook, AppSettings],
        )
        logger.info("MongoDB connection initialized in Celery worker")
    return _mongodb_client


async def get_app_settings() -> AppSettings:
    """
    Get application settings from database.

    Returns:
        AppSettings instance

    Raises:
        ValueError: If settings not found
    """
    await get_mongodb_client()
    app_settings = await AppSettings.find_one({"user_id": "default"})
    if not app_settings:
        raise ValueError("Application settings not found in database")
    return app_settings


def run_async(coro):
    """
    Run async coroutine in sync Celery task.

    Args:
        coro: Coroutine to run

    Returns:
        Coroutine result
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If loop is already running, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def _update_story_status(
    story_id: str,
    status: str,
    error_message: Optional[str] = None,
) -> None:
    """
    Update story status in database.

    Args:
        story_id: Story ID
        status: New status
        error_message: Optional error message
    """
    await get_mongodb_client()
    story = await Storybook.get(story_id)
    if story:
        story.status = status
        if error_message:
            story.error_message = error_message
        await story.save()
        logger.info(f"Story {story_id} status updated to: {status}")


async def _download_image_from_url(url: str) -> Optional[bytes]:
    """
    Download image bytes from a URL.

    Args:
        url: URL to download from (e.g., signed S3 URL)

    Returns:
        Image bytes or None if download fails
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return None


async def _generate_character_sheets(
    story: Storybook,
    metadata: StoryMetadata,
    image_provider: BaseImageProvider,
    safety_settings=None,
    max_characters: int = 3,
) -> Optional[List[bytes]]:
    """
    Generate character reference sheets for main characters.

    Creates clean character portrait images with neutral backgrounds
    to use as references for consistent character appearance across all pages.

    Args:
        story: Storybook instance
        metadata: Story metadata with character descriptions
        image_provider: Image generation provider
        safety_settings: Safety settings for image generation
        max_characters: Maximum number of character sheets to generate

    Returns:
        List of character sheet images as bytes, or None if generation fails
    """
    try:
        # Get main characters (protagonists first, then supporting)
        main_characters = [
            c for c in metadata.character_descriptions
            if c.role.lower() in ["protagonist", "main character"]
        ]

        # Add supporting characters if we don't have enough mains
        if len(main_characters) < max_characters:
            supporting = [
                c for c in metadata.character_descriptions
                if c.role.lower() not in ["protagonist", "main character"]
            ]
            main_characters.extend(supporting[:max_characters - len(main_characters)])

        main_characters = main_characters[:max_characters]

        if not main_characters:
            logger.warning("No characters found for character sheet generation")
            return None

        logger.info(f"Generating {len(main_characters)} character reference sheets")
        character_sheets = []

        for idx, character in enumerate(main_characters):
            logger.info(f"Generating character sheet {idx + 1}/{len(main_characters)}: {character.name}")

            prompt = f"""Create a character reference sheet for a children's storybook.

Character Name: {character.name}
Physical Description: {character.physical_description}
Personality: {character.personality}
Role: {character.role}

Illustration Style: {metadata.illustration_style_guide}
Target Age: {story.generation_inputs.audience_age} years old

IMPORTANT: Create a clean character portrait showing the character:
- Centered in the frame
- Facing forward in a neutral, standing pose
- Full body visible (head to toe)
- Plain white or very subtle background
- No text, labels, or annotations
- Focus on distinctive features, clothing, colors, and appearance details
- Clear, well-lit, easy to see all character details

This is a REFERENCE IMAGE for character consistency."""

            gen_kwargs = {
                "prompt": prompt,
                "aspect_ratio": "3:4",  # Portrait for character sheets
            }

            if safety_settings:
                gen_kwargs.update({
                    "safety_threshold": safety_settings.safety_threshold,
                    "allow_adult_imagery": safety_settings.allow_adult_imagery,
                    "bypass_safety_filters": safety_settings.bypass_safety_filters,
                })

            try:
                character_sheet_bytes = await image_provider.generate_image(**gen_kwargs)
                character_sheets.append(character_sheet_bytes)
                logger.info(f"Successfully generated character sheet for {character.name}")
            except Exception as e:
                error_msg = str(e).lower()
                if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                    logger.warning(f"Character sheet for {character.name} blocked by safety filters, skipping")
                else:
                    logger.error(f"Failed to generate character sheet for {character.name}: {e}")
                # Continue with other characters even if one fails

        if not character_sheets:
            logger.error("Failed to generate any character sheets")
            return None

        logger.info(f"Successfully generated {len(character_sheets)} character sheets")
        return character_sheets

    except Exception as e:
        logger.error(f"Error in character sheet generation: {e}")
        return None


@celery_app.task(name="generate_story", bind=True, max_retries=3)
def generate_story_task(self, story_id: str):
    """
    Main orchestration task for story generation.

    This task:
    1. Runs coordinator agent to plan the story
    2. Spawns parallel page generation tasks
    3. Validates the complete story
    4. Handles errors and retries

    Args:
        story_id: MongoDB document ID of the story to generate

    Returns:
        Success status dictionary
    """
    try:
        logger.info(f"Starting story generation for {story_id}")

        # Run async workflow
        result = run_async(_generate_story_workflow(story_id, self))

        logger.info(f"Story generation complete for {story_id}")
        return result

    except Exception as e:
        logger.error(f"Story generation failed for {story_id}: {e}")

        # Update story status to error
        try:
            run_async(_update_story_status(story_id, "error", str(e)))
        except Exception as update_error:
            logger.error(f"Failed to update error status: {update_error}")

        # Retry if not at max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying story generation (attempt {self.request.retries + 1})")
            raise self.retry(exc=e, countdown=60)  # Retry after 1 minute

        raise


async def _generate_story_workflow(story_id: str, task) -> dict:
    """
    Async workflow for story generation.

    Args:
        story_id: Story ID
        task: Celery task instance for progress updates

    Returns:
        Result dictionary
    """
    # Initialize MongoDB
    await get_mongodb_client()

    # Load story
    story = await Storybook.get(story_id)
    if not story:
        raise ValueError(f"Story {story_id} not found")

    # Update status to generating
    story.status = "generating"
    await story.save()

    # Get app settings from database
    app_settings = await get_app_settings()
    logger.info(f"Using API provider: {app_settings.primary_llm_provider.name}")

    # Step 1: Story Planning (Coordinator Agent)
    logger.info(f"Phase 1: Story planning for '{story.title}'")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "planning", "progress": 0.1, "message": "Planning story..."}
    )

    llm_provider = LLMProviderFactory.create_from_settings()
    image_provider = ImageProviderFactory.create_from_settings()
    coordinator = CoordinatorAgent(llm_provider)

    try:
        metadata = await coordinator.plan_story(story.generation_inputs)
        story.metadata = metadata

        # Update story title with generated title
        if metadata.title:
            story.title = metadata.title
            logger.info(f"Updated story title to: {metadata.title}")

        await story.save()

        logger.info(
            f"Story planning complete: {len(metadata.character_descriptions)} characters, "
            f"{len(metadata.page_outlines)} page outlines"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
            logger.error(f"Story planning blocked by safety filters: {e}")
            story.status = "error"
            story.error_message = "Content blocked by safety filters during planning. Please try a different topic or setting."
            await story.save()
            raise ValueError("Content blocked by safety filters during story planning")
        else:
            raise

    # Step 1.5: Generate Character Sheets for consistency
    logger.info("Phase 1.5: Generating character reference sheets")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "character_sheets", "progress": 0.2, "message": "Creating character reference sheets..."}
    )

    character_reference_bytes = await _generate_character_sheets(
        story=story,
        metadata=metadata,
        image_provider=image_provider,
        safety_settings=app_settings.safety_settings,
    )

    if character_reference_bytes:
        logger.info(f"Generated {len(character_reference_bytes)} character reference sheets")

        # Upload character sheets to storage
        character_sheet_urls = []
        for idx, sheet_bytes in enumerate(character_reference_bytes):
            try:
                character_name = metadata.character_descriptions[idx].name if idx < len(metadata.character_descriptions) else f"character_{idx}"
                filename = f"character_sheet_{idx}_{character_name.replace(' ', '_')}.png"

                object_key = await storage_service.upload_from_bytes(
                    story_id=str(story.id),
                    filename=filename,
                    data=sheet_bytes,
                    content_type="image/png",
                )

                presigned_url = await storage_service.get_signed_url(object_key, expiration=2592000)  # 30 days
                character_sheet_urls.append(presigned_url)
                logger.info(f"Uploaded character sheet {idx + 1}: {presigned_url}")
            except Exception as e:
                logger.error(f"Failed to upload character sheet {idx}: {e}")

        # Save character sheet URLs to story metadata
        if character_sheet_urls:
            story.metadata.character_sheet_urls = character_sheet_urls
            await story.save()
            logger.info(f"Saved {len(character_sheet_urls)} character sheet URLs to story metadata")
    else:
        logger.warning("Failed to generate character sheets, continuing without references")

    # Step 2: Page Generation (Page Agents in parallel)
    logger.info(f"Phase 2: Generating {story.generation_inputs.page_count} pages")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "page_generation", "progress": 0.3, "message": "Generating pages..."}
    )

    # Clear any existing pages (in case of retry)
    if story.pages:
        logger.warning(f"Clearing {len(story.pages)} existing pages from previous attempt")
        story.pages = []
        await story.save()

    page_generator = PageGeneratorAgent(llm_provider)

    # Generate pages sequentially (parallel generation would require more complex coordination)
    for i in range(story.generation_inputs.page_count):
        page_number = i + 1
        page_outline = metadata.page_outlines[i]

        logger.info(f"Generating page {page_number}/{story.generation_inputs.page_count}")

        try:
            page = await page_generator.generate_page(
                page_number=page_number,
                page_outline=page_outline,
                metadata=metadata,
                inputs=story.generation_inputs,
            )

            # Add page to story
            story.pages.append(page)
            await story.save()
        except Exception as e:
            error_msg = str(e).lower()
            if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                logger.error(f"Page {page_number} generation blocked by safety filters: {e}")
                story.status = "error"
                story.error_message = f"Content blocked by safety filters on page {page_number}. Please try a different topic or adjust your story settings."
                await story.save()
                raise ValueError(f"Content blocked by safety filters during page {page_number} generation")
            else:
                raise

        # Generate and upload illustration for this page
        try:
            logger.info(f"Generating illustration for page {page_number}")
            illustration_url = await _generate_page_illustration(
                page=page,
                story_id=str(story.id),
                image_provider=image_provider,
                safety_settings=app_settings.safety_settings,
                character_reference=character_reference_bytes,
                max_retries=settings.image_max_retries,
            )

            if illustration_url:
                # Update page with illustration URL
                page.illustration_url = illustration_url
                story.pages[-1] = page  # Update the last page in the list
                await story.save()
                logger.info(f"Illustration URL saved for page {page_number}")
            else:
                logger.warning(f"Failed to generate illustration for page {page_number}, continuing without it")

        except Exception as e:
            error_msg = str(e).lower()
            if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                logger.warning(f"Illustration for page {page_number} blocked by safety filters, continuing without image")
            else:
                logger.error(f"Error generating illustration for page {page_number}: {e}")
            # Continue without image (graceful degradation)

        # Update progress
        progress = 0.3 + (0.5 * (page_number / story.generation_inputs.page_count))
        task.update_state(
            state="PROGRESS",
            meta={
                "phase": "page_generation",
                "progress": progress,
                "message": f"Generated page {page_number}/{story.generation_inputs.page_count}"
            }
        )

    logger.info(f"All {len(story.pages)} pages generated")

    # Step 3: Validation
    logger.info(f"Phase 3: Validating story '{story.title}'")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "validation", "progress": 0.85, "message": "Validating story..."}
    )

    validator = ValidatorAgent(llm_provider)

    try:
        validation_output = await validator.validate_story(story)
    except Exception as e:
        # If validation fails due to content blocking, skip validation
        if "blocked" in str(e).lower() or "safety" in str(e).lower():
            logger.warning(f"Validation blocked by safety filters: {e}")
            logger.warning("Skipping validation and marking story as complete")

            # Mark story as complete without validation
            story.status = "complete"
            await story.save()

            # Try to generate cover image
            try:
                logger.info("Generating cover image...")
                cover_url = await _generate_cover_image(
                    story=story,
                    image_provider=image_provider,
                    safety_settings=app_settings.safety_settings,
                )

                if cover_url:
                    story.cover_image_url = cover_url
                    await story.save()
                    logger.info(f"Cover image URL saved: {cover_url}")
            except Exception as cover_error:
                logger.error(f"Error generating cover image: {cover_error}")

            # Return success without validation
            logger.info(f"Story generation complete for {story_id} (validation skipped)")
            return {
                "status": "success",
                "story_id": story_id,
                "title": story.title,
                "pages": len(story.pages),
                "validation": {
                    "is_valid": None,
                    "quality": "Validation skipped due to content filters",
                    "issues": 0
                }
            }
        else:
            # Re-raise other errors
            raise

    # Handle validation results
    if validation_output.is_valid:
        logger.info(f"Story '{story.title}' passed validation")
        # Mark all pages as validated
        for page in story.pages:
            page.validated = True
        story.status = "complete"
        await story.save()

        # Generate cover image
        try:
            logger.info("Generating cover image...")
            cover_url = await _generate_cover_image(
                story=story,
                image_provider=image_provider,
                safety_settings=app_settings.safety_settings,
            )

            if cover_url:
                story.cover_image_url = cover_url
                await story.save()
                logger.info(f"Cover image URL saved: {cover_url}")
            else:
                logger.warning("Failed to generate cover image, continuing without it")

        except Exception as e:
            error_msg = str(e).lower()
            if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                logger.warning(f"Cover image blocked by safety filters, continuing without it")
            else:
                logger.error(f"Error generating cover image: {e}")
            # Continue without cover (graceful degradation)

    else:
        logger.warning(
            f"Story '{story.title}' failed validation with "
            f"{len(validation_output.issues)} issues"
        )

        # Get pages that need regeneration
        pages_to_regenerate = validator.get_pages_needing_regeneration(validation_output)

        if pages_to_regenerate:
            logger.info(f"Regenerating {len(pages_to_regenerate)} pages")
            total_regen = len(pages_to_regenerate)

            # Regenerate problematic pages
            for regen_index, (page_number, issue_description) in enumerate(pages_to_regenerate):
                # Update progress for regeneration
                regen_progress = 0.85 + (0.1 * ((regen_index + 1) / total_regen))
                task.update_state(
                    state="PROGRESS",
                    meta={
                        "phase": "regeneration",
                        "progress": regen_progress,
                        "message": f"Regenerating page {page_number} ({regen_index + 1}/{total_regen})"
                    }
                )

                # Find the page
                page_index = page_number - 1
                if page_index < len(story.pages):
                    old_page = story.pages[page_index]

                    # Check retry limit
                    if old_page.generation_attempts >= settings.default_retry_limit:
                        logger.warning(
                            f"Page {page_number} exceeded retry limit "
                            f"({old_page.generation_attempts} attempts)"
                        )
                        continue

                    # Regenerate page
                    logger.info(f"Regenerating page {page_number} due to: {issue_description}")
                    new_page = await page_generator.regenerate_page(
                        page=old_page,
                        issue_description=issue_description,
                        metadata=metadata,
                        inputs=story.generation_inputs,
                    )

                    # Generate illustration for regenerated page
                    try:
                        logger.info(f"Generating illustration for regenerated page {page_number}")
                        illustration_url = await _generate_page_illustration(
                            page=new_page,
                            story_id=str(story.id),
                            image_provider=image_provider,
                            safety_settings=app_settings.safety_settings,
                            character_reference=character_reference_bytes,
                            max_retries=settings.image_max_retries,
                        )

                        if illustration_url:
                            new_page.illustration_url = illustration_url
                            story.pages[page_index] = new_page
                            await story.save()
                            logger.info(f"Illustration saved for regenerated page {page_number}")
                        else:
                            logger.error(f"Failed to generate illustration for regenerated page {page_number}")
                            # Replace page even without illustration
                            story.pages[page_index] = new_page
                            await story.save()

                    except Exception as e:
                        logger.error(f"Failed to generate illustration for regenerated page {page_number}: {e}")
                        # Replace page even without illustration
                        story.pages[page_index] = new_page
                        await story.save()

            # Re-validate after regeneration
            task.update_state(
                state="PROGRESS",
                meta={"phase": "revalidation", "progress": 0.95, "message": "Re-validating story..."}
            )
            validation_output = await validator.validate_story(story)

            if validation_output.is_valid:
                logger.info("Story passed validation after regeneration")
                for page in story.pages:
                    page.validated = True
                story.status = "complete"
            else:
                logger.warning("Story still has issues after regeneration")
                # Mark as complete anyway (minor issues acceptable)
                story.status = "complete"

            await story.save()

            # Generate cover image after regeneration
            try:
                logger.info("Generating cover image after regeneration...")
                cover_url = await _generate_cover_image(
                    story=story,
                    image_provider=image_provider,
                    safety_settings=app_settings.safety_settings,
                )

                if cover_url:
                    story.cover_image_url = cover_url
                    await story.save()
                    logger.info(f"Cover image URL saved: {cover_url}")
                else:
                    logger.warning("Failed to generate cover image, continuing without it")

            except Exception as e:
                error_msg = str(e).lower()
                if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                    logger.warning(f"Cover image blocked by safety filters, continuing without it")
                else:
                    logger.error(f"Error generating cover image: {e}")
                # Continue without cover (graceful degradation)

        else:
            # Only minor issues, mark as complete
            logger.info("Only minor issues found, marking as complete")
            story.status = "complete"
            await story.save()

            # Generate cover image for minor issues case
            try:
                logger.info("Generating cover image...")
                cover_url = await _generate_cover_image(
                    story=story,
                    image_provider=image_provider,
                    safety_settings=app_settings.safety_settings,
                )

                if cover_url:
                    story.cover_image_url = cover_url
                    await story.save()
                    logger.info(f"Cover image URL saved: {cover_url}")
                else:
                    logger.warning("Failed to generate cover image, continuing without it")

            except Exception as e:
                error_msg = str(e).lower()
                if "blocked" in error_msg or "safety" in error_msg or "prohibited" in error_msg:
                    logger.warning(f"Cover image blocked by safety filters, continuing without it")
                else:
                    logger.error(f"Error generating cover image: {e}")
                # Continue without cover (graceful degradation)

    task.update_state(
        state="PROGRESS",
        meta={"phase": "complete", "progress": 1.0, "message": "Story generation complete"}
    )

    return {
        "status": "success",
        "story_id": str(story.id),
        "title": story.title,
        "pages": len(story.pages),
        "validation": {
            "is_valid": validation_output.is_valid,
            "quality": validation_output.overall_quality,
            "issues": len(validation_output.issues),
        }
    }


@celery_app.task(name="generate_page", bind=True, max_retries=3)
def generate_page_task(self, story_id: str, page_number: int):
    """
    Task for generating a single page.

    This is designed for parallel page generation but currently
    not used (pages generated sequentially for better context).

    Args:
        story_id: Story ID
        page_number: Page number to generate

    Returns:
        Generated page dictionary
    """
    try:
        logger.info(f"Generating page {page_number} for story {story_id}")

        result = run_async(_generate_page_workflow(story_id, page_number))

        logger.info(f"Page {page_number} generation complete")
        return result

    except Exception as e:
        logger.error(f"Page {page_number} generation failed: {e}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)

        raise


async def _generate_page_workflow(story_id: str, page_number: int) -> dict:
    """
    Async workflow for page generation.

    Args:
        story_id: Story ID
        page_number: Page number

    Returns:
        Page data dictionary
    """
    # Initialize MongoDB
    await get_mongodb_client()

    # Load story
    story = await Storybook.get(story_id)
    if not story:
        raise ValueError(f"Story {story_id} not found")

    # Get page outline
    page_outline = story.metadata.page_outlines[page_number - 1]

    # Generate page
    llm_provider = LLMProviderFactory.create_from_settings()
    page_generator = PageGeneratorAgent(llm_provider)

    page = await page_generator.generate_page(
        page_number=page_number,
        page_outline=page_outline,
        metadata=story.metadata,
        inputs=story.generation_inputs,
    )

    # Add to story (thread-safe append)
    story.pages.append(page)
    await story.save()

    return {
        "page_number": page.page_number,
        "text_length": len(page.text) if page.text else 0,
        "has_illustration_prompt": page.illustration_prompt is not None,
    }


@celery_app.task(name="validate_story", bind=True, max_retries=2)
def validate_story_task(self, story_id: str):
    """
    Task for validating a complete story.

    Args:
        story_id: Story ID

    Returns:
        Validation result dictionary
    """
    try:
        logger.info(f"Validating story {story_id}")

        result = run_async(_validate_story_workflow(story_id))

        logger.info(f"Story validation complete")
        return result

    except Exception as e:
        logger.error(f"Story validation failed: {e}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)

        raise


async def _validate_story_workflow(story_id: str) -> dict:
    """
    Async workflow for story validation.

    Args:
        story_id: Story ID

    Returns:
        Validation result dictionary
    """
    # Initialize MongoDB
    await get_mongodb_client()

    # Load story
    story = await Storybook.get(story_id)
    if not story:
        raise ValueError(f"Story {story_id} not found")

    # Validate
    llm_provider = LLMProviderFactory.create_from_settings()
    validator = ValidatorAgent(llm_provider)

    validation_output = await validator.validate_story(story)

    return {
        "is_valid": validation_output.is_valid,
        "overall_quality": validation_output.overall_quality,
        "issues_count": len(validation_output.issues),
        "issues": [
            {
                "page": issue.page_number,
                "type": issue.issue_type,
                "severity": issue.severity,
                "description": issue.description,
            }
            for issue in validation_output.issues
        ],
        "suggestions": validation_output.suggestions,
    }


async def _generate_page_illustration(
    page: Page,
    story_id: str,
    image_provider: BaseImageProvider,
    safety_settings=None,
    character_reference: Optional[List[bytes]] = None,
    max_retries: int = 3,
) -> Optional[str]:
    """
    Generate and upload illustration for a page with retry logic.

    Args:
        page: Page with illustration_prompt
        story_id: Story ID for storage path
        image_provider: Image generation provider
        safety_settings: Safety settings for image generation
        character_reference: List of character sheet images for consistency
        max_retries: Maximum number of retry attempts

    Returns:
        Signed URL to the uploaded illustration, or None if generation fails

    Raises:
        Exception: If all retries are exhausted
    """
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Generating illustration for page {page.page_number} "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            # Build generation kwargs
            gen_kwargs = {
                "prompt": page.illustration_prompt,
                "aspect_ratio": settings.image_aspect_ratio,
            }

            # Add character reference sheets if provided
            if character_reference:
                gen_kwargs["reference_images"] = character_reference
                logger.debug(f"Using {len(character_reference)} character reference sheets for consistency")

            # Add safety settings if provided
            if safety_settings:
                gen_kwargs.update({
                    "safety_threshold": safety_settings.safety_threshold,
                    "allow_adult_imagery": safety_settings.allow_adult_imagery,
                    "bypass_safety_filters": safety_settings.bypass_safety_filters,
                })

            # Generate image from prompt
            illustration_bytes = await image_provider.generate_image(**gen_kwargs)

            logger.info(
                f"Generated illustration for page {page.page_number} "
                f"({len(illustration_bytes)} bytes)"
            )

            # Upload to storage
            filename = f"page_{page.page_number}.png"
            object_key = await storage_service.upload_from_bytes(
                story_id=story_id,
                filename=filename,
                data=illustration_bytes,
                content_type="image/png",
            )

            logger.info(f"Uploaded illustration for page {page.page_number}: {object_key}")

            # Get signed URL (30 days expiration)
            illustration_url = await storage_service.get_signed_url(
                object_key=object_key,
                expiration=86400 * 30,  # 30 days
            )

            return illustration_url

        except Exception as e:
            logger.error(
                f"Failed to generate illustration for page {page.page_number} "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )

            if attempt >= max_retries - 1:
                # All retries exhausted
                logger.error(
                    f"Exhausted all {max_retries} retries for page {page.page_number} illustration"
                )
                return None

            # Exponential backoff
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)

    return None


async def _generate_cover_image(
    story: Storybook,
    image_provider: BaseImageProvider,
    safety_settings=None,
) -> Optional[str]:
    """
    Generate cover image with title overlay.

    Args:
        story: Complete storybook with metadata
        image_provider: Image generation provider
        safety_settings: Safety settings for image generation

    Returns:
        Signed URL to the uploaded cover image, or None if generation fails
    """
    try:
        logger.info(f"Generating cover image for '{story.title}'")

        # Build cover prompt from story metadata
        cover_prompt = _build_cover_prompt(story)

        # Build generation kwargs
        gen_kwargs = {
            "prompt": cover_prompt,
            "aspect_ratio": settings.cover_aspect_ratio,
        }

        # Add safety settings if provided
        if safety_settings:
            gen_kwargs.update({
                "safety_threshold": safety_settings.safety_threshold,
                "allow_adult_imagery": safety_settings.allow_adult_imagery,
                "bypass_safety_filters": safety_settings.bypass_safety_filters,
            })

        # Generate cover image with title included (Gemini includes title in image)
        cover_bytes = await image_provider.generate_image(**gen_kwargs)

        logger.info(f"Generated cover image ({len(cover_bytes)} bytes)")

        # Upload to storage (no text overlay needed - Gemini includes the title)
        object_key = await storage_service.upload_from_bytes(
            story_id=str(story.id),
            filename="cover.png",
            data=cover_bytes,
            content_type="image/png",
        )

        logger.info(f"Uploaded cover image: {object_key}")

        # Get signed URL (30 days expiration)
        cover_url = await storage_service.get_signed_url(
            object_key=object_key,
            expiration=86400 * 30,  # 30 days
        )

        return cover_url

    except Exception as e:
        logger.error(f"Failed to generate cover image: {e}")
        return None


def _build_cover_prompt(story: Storybook) -> str:
    """
    Build cover image prompt from story metadata.

    Creates a detailed prompt that captures the essence of the story
    for generating an eye-catching cover illustration.

    Args:
        story: Storybook with metadata and inputs

    Returns:
        Cover image prompt string
    """
    metadata = story.metadata
    inputs = story.generation_inputs

    # Get main characters (protagonists first)
    main_chars = [
        c for c in metadata.character_descriptions
        if c.role == "protagonist"
    ][:2]  # Limit to 2 main characters

    # Build character description
    if main_chars:
        char_desc = ", ".join([
            f"{c.name} ({c.physical_description})"
            for c in main_chars
        ])
    else:
        char_desc = "the main character"

    # Build comprehensive cover prompt
    prompt = f"""Create a captivating storybook cover illustration for "{story.title}".

Setting: {inputs.setting}
Main Characters: {char_desc}
Story Theme: {inputs.topic}
Illustration Style: {metadata.illustration_style_guide}
Target Age: {inputs.audience_age} years old

The cover should be eye-catching and magical, showing the main characters in the story's
primary setting. The composition should be dramatic and inviting, drawing young readers in.

IMPORTANT: Include the book title "{story.title}" prominently on the cover in large,
child-friendly lettering. The title should be clearly readable and integrated into the
design as part of the illustration. Use colors that contrast well with the background.

The overall mood should be {inputs.setting.split()[0] if inputs.setting else "magical"} and
adventurous, perfectly capturing the essence of this children's {inputs.format}."""

    return prompt
