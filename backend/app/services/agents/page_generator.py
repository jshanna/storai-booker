"""Page generator agent for creating individual page content."""
from loguru import logger

from app.models.storybook import (
    GenerationInputs,
    StoryMetadata,
    Page,
    Panel,
    DialogueEntry,
    SoundEffect,
)
from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompts.page_generation import (
    build_page_generation_prompt,
    PageGenerationOutput,
)
from app.services.llm.prompts.comic_page_generation import (
    build_comic_page_generation_prompt,
    ComicPageGenerationOutput,
)

# Valid position values for dialogue and sound effects
VALID_POSITIONS = {
    "top-left", "top-center", "top-right",
    "middle-left", "middle-center", "middle-right",
    "bottom-left", "bottom-center", "bottom-right",
}

# Map common LLM position mistakes to valid values
POSITION_ALIASES = {
    "center": "middle-center",
    "middle": "middle-center",
    "top": "top-center",
    "bottom": "bottom-center",
    "left": "middle-left",
    "right": "middle-right",
    "topleft": "top-left",
    "topright": "top-right",
    "bottomleft": "bottom-left",
    "bottomright": "bottom-right",
}


def normalize_position(position: str) -> str:
    """Normalize a position string to a valid panel position value."""
    pos = position.lower().strip()
    if pos in VALID_POSITIONS:
        return pos
    if pos in POSITION_ALIASES:
        return POSITION_ALIASES[pos]
    # Default fallback
    logger.warning(f"Unknown position '{position}', defaulting to 'middle-center'")
    return "middle-center"


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

    async def generate_comic_page(
        self,
        page_number: int,
        page_outline: str,
        metadata: StoryMetadata,
        inputs: GenerationInputs,
    ) -> Page:
        """
        Generate content for a comic page with panels.

        Args:
            page_number: Page number (1-indexed)
            page_outline: Outline for this page from story planning
            metadata: Complete story metadata
            inputs: Original user inputs

        Returns:
            Page object with panels array populated

        Raises:
            Exception: If page generation fails
        """
        try:
            logger.info(
                f"Generating comic page {page_number}/{inputs.page_count} "
                f"with {inputs.panels_per_page or 4} panels"
            )

            # Build the comic page generation prompt
            prompt = build_comic_page_generation_prompt(
                page_number=page_number,
                page_outline=page_outline,
                metadata=metadata,
                inputs=inputs,
            )

            # Generate structured output from LLM
            comic_output: ComicPageGenerationOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=ComicPageGenerationOutput,
            )

            # Convert LLM output to model objects
            panels = []
            for panel_out in comic_output.panels:
                # Convert dialogue entries (normalize positions)
                dialogue = [
                    DialogueEntry(
                        character=d.character,
                        text=d.text,
                        position=normalize_position(d.position),
                        style=d.style,
                    )
                    for d in panel_out.dialogue
                ]

                # Convert sound effects (normalize positions)
                sound_effects = [
                    SoundEffect(
                        text=s.text,
                        position=normalize_position(s.position),
                        style=s.style,
                    )
                    for s in panel_out.sound_effects
                ]

                panel = Panel(
                    panel_number=panel_out.panel_number,
                    illustration_prompt=panel_out.illustration_prompt,
                    illustration_url=None,  # Set during image generation
                    dialogue=dialogue,
                    caption=panel_out.caption,
                    sound_effects=sound_effects,
                    aspect_ratio="1:1",  # Default, can be customized per layout
                    generation_attempts=1,
                    validated=False,
                )
                panels.append(panel)

            logger.info(
                f"Comic page {page_number} generated: "
                f"{len(panels)} panels, layout: {comic_output.layout}"
            )

            # Create Page object with panels
            page = Page(
                page_number=page_number,
                text=None,  # Comics use panels, not page text
                illustration_prompt=None,  # Each panel has its own prompt
                illustration_url=None,  # Comics use panel images
                panels=panels,
                layout=comic_output.layout,
                generation_attempts=1,
                validated=False,
            )

            return page

        except Exception as e:
            logger.error(f"Comic page {page_number} generation failed: {e}")
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
