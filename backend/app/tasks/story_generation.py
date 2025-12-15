"""Story generation Celery tasks."""
import asyncio
from typing import Optional
from celery import group, chord
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.services.celery_app import celery_app
from app.core.config import settings
from app.models.storybook import Storybook, Page
from app.services.llm.provider_factory import LLMProviderFactory
from app.services.agents.coordinator import CoordinatorAgent
from app.services.agents.page_generator import PageGeneratorAgent
from app.services.agents.validator import ValidatorAgent
from app.services.image.provider_factory import ImageProviderFactory
from app.services.image.compositor import ImageCompositor
from app.services.image.base import BaseImageProvider
from app.services.storage import storage_service


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
            document_models=[Storybook],
        )
        logger.info("MongoDB connection initialized in Celery worker")
    return _mongodb_client


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

    # Step 1: Story Planning (Coordinator Agent)
    logger.info(f"Phase 1: Story planning for '{story.title}'")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "planning", "progress": 0.1, "message": "Planning story..."}
    )

    llm_provider = LLMProviderFactory.create_from_settings()
    image_provider = ImageProviderFactory.create_from_settings()
    coordinator = CoordinatorAgent(llm_provider)

    metadata = await coordinator.plan_story(story.generation_inputs)
    story.metadata = metadata
    await story.save()

    logger.info(
        f"Story planning complete: {len(metadata.character_descriptions)} characters, "
        f"{len(metadata.page_outlines)} page outlines"
    )

    # Step 2: Page Generation (Page Agents in parallel)
    logger.info(f"Phase 2: Generating {story.generation_inputs.page_count} pages")
    task.update_state(
        state="PROGRESS",
        meta={"phase": "page_generation", "progress": 0.3, "message": "Generating pages..."}
    )

    page_generator = PageGeneratorAgent(llm_provider)

    # Generate pages sequentially (parallel generation would require more complex coordination)
    for i in range(story.generation_inputs.page_count):
        page_number = i + 1
        page_outline = metadata.page_outlines[i]

        logger.info(f"Generating page {page_number}/{story.generation_inputs.page_count}")

        page = await page_generator.generate_page(
            page_number=page_number,
            page_outline=page_outline,
            metadata=metadata,
            inputs=story.generation_inputs,
        )

        # Add page to story
        story.pages.append(page)
        await story.save()

        # Generate and upload illustration for this page
        try:
            logger.info(f"Generating illustration for page {page_number}")
            illustration_url = await _generate_page_illustration(
                page=page,
                story_id=str(story.id),
                image_provider=image_provider,
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
    validation_output = await validator.validate_story(story)

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
            )

            if cover_url:
                story.cover_image_url = cover_url
                await story.save()
                logger.info(f"Cover image URL saved: {cover_url}")
            else:
                logger.warning("Failed to generate cover image, continuing without it")

        except Exception as e:
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

            # Regenerate problematic pages
            for page_number, issue_description in pages_to_regenerate:
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
                    new_page = await page_generator.regenerate_page(
                        page=old_page,
                        issue_description=issue_description,
                        metadata=metadata,
                        inputs=story.generation_inputs,
                    )

                    # Replace page
                    story.pages[page_index] = new_page
                    await story.save()

            # Re-validate after regeneration
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
                )

                if cover_url:
                    story.cover_image_url = cover_url
                    await story.save()
                    logger.info(f"Cover image URL saved: {cover_url}")
                else:
                    logger.warning("Failed to generate cover image, continuing without it")

            except Exception as e:
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
                )

                if cover_url:
                    story.cover_image_url = cover_url
                    await story.save()
                    logger.info(f"Cover image URL saved: {cover_url}")
                else:
                    logger.warning("Failed to generate cover image, continuing without it")

            except Exception as e:
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
    max_retries: int = 3,
) -> Optional[str]:
    """
    Generate and upload illustration for a page with retry logic.

    Args:
        page: Page with illustration_prompt
        story_id: Story ID for storage path
        image_provider: Image generation provider
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

            # Generate image from prompt
            illustration_bytes = await image_provider.generate_image(
                prompt=page.illustration_prompt,
                aspect_ratio=settings.image_aspect_ratio,
            )

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
) -> Optional[str]:
    """
    Generate cover image with title overlay.

    Args:
        story: Complete storybook with metadata
        image_provider: Image generation provider

    Returns:
        Signed URL to the uploaded cover image, or None if generation fails
    """
    try:
        logger.info(f"Generating cover image for '{story.title}'")

        # Build cover prompt from story metadata
        cover_prompt = _build_cover_prompt(story)

        # Generate base cover image (portrait aspect ratio)
        cover_bytes = await image_provider.generate_image(
            prompt=cover_prompt,
            aspect_ratio=settings.cover_aspect_ratio,
        )

        logger.info(f"Generated base cover image ({len(cover_bytes)} bytes)")

        # Composite title overlay
        compositor = ImageCompositor(font_path=settings.cover_font_path)
        final_cover = await compositor.create_cover_with_title(
            image_bytes=cover_bytes,
            title=story.title,
        )

        logger.info(f"Composited title overlay ({len(final_cover)} bytes)")

        # Upload to storage
        object_key = await storage_service.upload_from_bytes(
            story_id=str(story.id),
            filename="cover.png",
            data=final_cover,
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
Leave the bottom third of the image relatively clear and uncluttered for title text overlay.

The overall mood should be {inputs.setting.split()[0] if inputs.setting else "magical"} and
adventurous, perfectly capturing the essence of this children's {inputs.format}."""

    return prompt
