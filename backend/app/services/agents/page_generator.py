"""Page generator agent for creating individual page content."""
from loguru import logger

from app.models.storybook import GenerationInputs, StoryMetadata, Page
from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompts.page_generation import (
    build_page_generation_prompt,
    PageGenerationOutput,
)


class PageGeneratorAgent:
    """
    Page generation agent responsible for creating individual pages.

    This agent takes a page outline and generates:
    - Narrative text for the page
    - Detailed illustration prompt
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize page generator agent.

        Args:
            llm_provider: LLM provider instance for text generation
        """
        self.llm = llm_provider
        logger.info(f"Initialized PageGeneratorAgent with {self.llm}")

    async def generate_page(
        self,
        page_number: int,
        page_outline: str,
        metadata: StoryMetadata,
        inputs: GenerationInputs,
    ) -> Page:
        """
        Generate content for a single page.

        Args:
            page_number: Page number (1-indexed)
            page_outline: Outline for this page from story planning
            metadata: Complete story metadata
            inputs: Original user inputs

        Returns:
            Page object with text and illustration_prompt populated

        Raises:
            Exception: If page generation fails
        """
        try:
            logger.info(f"Generating page {page_number}/{inputs.page_count}")

            # Build the page generation prompt
            prompt = build_page_generation_prompt(
                page_number=page_number,
                page_outline=page_outline,
                metadata=metadata,
                inputs=inputs,
            )

            # Generate structured output from LLM
            page_output: PageGenerationOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=PageGenerationOutput,
            )

            logger.info(
                f"Page {page_number} generated: "
                f"{len(page_output.page_text)} chars text, "
                f"{len(page_output.illustration_prompt)} chars prompt"
            )

            # Create Page object
            page = Page(
                page_number=page_number,
                text=page_output.page_text,
                illustration_prompt=page_output.illustration_prompt,
                illustration_url=None,  # Phase 3: Image generation
                generation_attempts=1,
                validated=False,  # Will be set by validator
            )

            logger.debug(f"Page {page_number} text: {page.text[:100]}...")

            return page

        except Exception as e:
            logger.error(f"Page {page_number} generation failed: {e}")
            raise

    async def regenerate_page(
        self,
        page: Page,
        issue_description: str,
        metadata: StoryMetadata,
        inputs: GenerationInputs,
    ) -> Page:
        """
        Regenerate a page that failed validation.

        Args:
            page: Original page that needs regeneration
            issue_description: Description of what was wrong
            metadata: Story metadata
            inputs: Original user inputs

        Returns:
            New Page object with corrected content

        Raises:
            Exception: If regeneration fails
        """
        try:
            logger.warning(
                f"Regenerating page {page.page_number} due to: {issue_description}"
            )

            # Get the page outline
            page_outline = metadata.page_outlines[page.page_number - 1]

            # Build prompt with feedback
            base_prompt = build_page_generation_prompt(
                page_number=page.page_number,
                page_outline=page_outline,
                metadata=metadata,
                inputs=inputs,
            )

            # Add feedback about the issue
            prompt_with_feedback = f"""{base_prompt}

**Previous Attempt Had Issues:**
{issue_description}

Please correct these issues in your new generation."""

            # Generate new version
            page_output: PageGenerationOutput = await self.llm.generate_structured(
                prompt=prompt_with_feedback,
                response_model=PageGenerationOutput,
            )

            # Create new Page object with incremented attempts
            new_page = Page(
                page_number=page.page_number,
                text=page_output.page_text,
                illustration_prompt=page_output.illustration_prompt,
                illustration_url=None,
                generation_attempts=page.generation_attempts + 1,
                validated=False,
            )

            logger.info(
                f"Page {page.page_number} regenerated "
                f"(attempt {new_page.generation_attempts})"
            )

            return new_page

        except Exception as e:
            logger.error(f"Page {page.page_number} regeneration failed: {e}")
            raise
