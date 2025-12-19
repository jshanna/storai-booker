"""Base class for vision-based critic agents."""

from abc import ABC, abstractmethod
from typing import Type, Dict, Any
from pydantic import BaseModel
from loguru import logger

from app.services.llm.base import BaseLLMProvider


class BaseCriticAgent(ABC):
    """
    Base class for vision-based critic agents that review generated comic pages.

    All critic agents analyze the actual generated image using multimodal LLM
    capabilities and return structured feedback for potential regeneration.
    """

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize the critic agent.

        Args:
            llm_provider: LLM provider with vision capabilities
        """
        self.llm = llm_provider

    @property
    @abstractmethod
    def critic_name(self) -> str:
        """Name of this critic for logging."""
        pass

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseModel]:
        """Pydantic model for this critic's output."""
        pass

    @abstractmethod
    def build_review_prompt(
        self,
        page_script: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> str:
        """
        Build the review prompt for this critic.

        Args:
            page_script: Script data for the page (panels, dialogue, etc.)
            story_context: Context about the story (title, age, style, etc.)

        Returns:
            Prompt string for vision-based analysis
        """
        pass

    async def review(
        self,
        image_bytes: bytes,
        page_script: Dict[str, Any],
        story_context: Dict[str, Any],
    ) -> BaseModel:
        """
        Review a generated comic page image.

        Args:
            image_bytes: The generated page image as bytes
            page_script: Script data for the page including:
                - panels: List of panel data with dialogue, captions, etc.
                - layout: Layout description (e.g., "2x2", "1-2")
                - page_number: Page number in the story
            story_context: Context about the story including:
                - title: Story title
                - target_age: Target audience age
                - illustration_style: Requested art style
                - page_number: Current page number
                - total_pages: Total pages in story

        Returns:
            Critic output model with scores, feedback, and suggestions
        """
        try:
            logger.info(
                f"{self.critic_name} reviewing page {story_context.get('page_number', '?')}"
            )

            # Build the review prompt
            prompt = self.build_review_prompt(page_script, story_context)

            # Call vision-structured generation
            result = await self.llm.generate_vision_structured(
                prompt=prompt,
                image_bytes=image_bytes,
                response_model=self.response_model,
            )

            logger.info(
                f"{self.critic_name} completed: score={result.score}/10"
            )

            return result

        except Exception as e:
            logger.error(f"{self.critic_name} review failed: {e}")
            # Return a default "pass" response if critic fails
            # This allows generation to continue without blocking
            return self._create_fallback_response(str(e))

    @abstractmethod
    def _create_fallback_response(self, error_message: str) -> BaseModel:
        """
        Create a fallback response when review fails.

        Should return a "passing" score to avoid blocking generation.

        Args:
            error_message: The error that occurred

        Returns:
            Default critic output with passing score
        """
        pass

    def _format_panel_info(self, page_script: Dict[str, Any]) -> str:
        """
        Format panel information for the prompt.

        Args:
            page_script: Page script data

        Returns:
            Formatted string describing the panels
        """
        panels = page_script.get("panels", [])
        if not panels:
            return "No panel information available."

        lines = []
        for panel in panels:
            panel_num = panel.get("panel_number", "?")
            prompt = panel.get("illustration_prompt", "")[:100]
            dialogue_count = len(panel.get("dialogue", []))
            caption = "Yes" if panel.get("caption") else "No"

            lines.append(
                f"  Panel {panel_num}: {prompt}... "
                f"(Dialogue: {dialogue_count}, Caption: {caption})"
            )

        return "\n".join(lines)

    def _format_story_context(self, story_context: Dict[str, Any]) -> str:
        """
        Format story context for the prompt.

        Args:
            story_context: Story context data

        Returns:
            Formatted string with story info
        """
        return f"""Story: {story_context.get('title', 'Unknown')}
Target Age: {story_context.get('target_age', 'Unknown')} years old
Illustration Style: {story_context.get('illustration_style', 'Unknown')}
Page: {story_context.get('page_number', '?')} of {story_context.get('total_pages', '?')}"""
