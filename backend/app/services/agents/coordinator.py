"""Coordinating agent for initial story planning."""
from loguru import logger

from app.models.storybook import GenerationInputs, StoryMetadata, CharacterDescription
from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompts.story_planning import (
    build_story_planning_prompt,
    StoryPlanningOutput,
)


class CoordinatorAgent:
    """
    Coordinating agent responsible for Phase 1 of story generation.

    This agent takes user inputs and creates a complete story plan including:
    - Expanded character descriptions
    - Character relationship mapping
    - Overall story outline
    - Per-page outlines
    - Illustration style guide
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize coordinator agent.

        Args:
            llm_provider: LLM provider instance for text generation
        """
        self.llm = llm_provider
        logger.info(f"Initialized CoordinatorAgent with {self.llm}")

    async def plan_story(self, inputs: GenerationInputs) -> StoryMetadata:
        """
        Generate complete story plan from user inputs.

        Args:
            inputs: User-provided generation parameters

        Returns:
            Complete StoryMetadata with all planning fields populated

        Raises:
            Exception: If planning fails
        """
        try:
            logger.info(
                f"Starting story planning for '{inputs.topic}' "
                f"(age {inputs.audience_age}, {inputs.page_count} pages)"
            )

            # Build the planning prompt
            prompt = build_story_planning_prompt(inputs)

            # Generate structured output from LLM
            planning_output: StoryPlanningOutput = await self.llm.generate_structured(
                prompt=prompt,
                response_model=StoryPlanningOutput,
            )

            logger.info(
                f"Story planning complete: "
                f"{len(planning_output.character_descriptions)} characters, "
                f"{len(planning_output.page_outlines)} pages"
            )

            # Validate we got the right number of page outlines
            if len(planning_output.page_outlines) != inputs.page_count:
                logger.warning(
                    f"Expected {inputs.page_count} page outlines, "
                    f"got {len(planning_output.page_outlines)}. Adjusting..."
                )

                # Pad or trim to match requested page count
                if len(planning_output.page_outlines) < inputs.page_count:
                    # Add generic outlines for missing pages
                    for i in range(len(planning_output.page_outlines), inputs.page_count):
                        planning_output.page_outlines.append(
                            f"Page {i + 1}: Continue the story..."
                        )
                else:
                    # Trim extra outlines
                    planning_output.page_outlines = planning_output.page_outlines[:inputs.page_count]

            # Convert to StoryMetadata
            metadata = StoryMetadata(
                title=planning_output.title,
                character_descriptions=planning_output.character_descriptions,
                character_relations=planning_output.character_relations,
                story_outline=planning_output.story_outline,
                page_outlines=planning_output.page_outlines,
                illustration_style_guide=planning_output.illustration_style_guide,
            )

            logger.debug(f"Story outline: {metadata.story_outline[:100]}...")

            return metadata

        except Exception as e:
            logger.error(f"Story planning failed: {e}")
            raise
