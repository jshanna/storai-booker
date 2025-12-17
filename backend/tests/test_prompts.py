"""Tests for LLM prompt templates."""
import pytest
from pydantic import ValidationError

from app.models.storybook import GenerationInputs, CharacterDescription
from app.services.llm.prompts.story_planning import (
    build_story_planning_prompt,
    _get_age_guidelines,
)
from app.services.llm.prompts.page_generation import (
    build_page_generation_prompt,
)
from app.services.llm.prompts.validation import (
    build_validation_prompt,
)


class TestStoryPlanningPrompts:
    """Tests for story planning prompt generation."""

    def test_build_story_planning_prompt_basic(self):
        """Test basic story planning prompt generation."""
        inputs = GenerationInputs(
            audience_age=7,
            topic="A brave squirrel",
            setting="Magical forest",
            format="storybook",
            illustration_style="watercolor",
            characters=["Hazel"],
            page_count=5
        )

        prompt = build_story_planning_prompt(inputs)

        assert "7-year-old" in prompt
        assert "A brave squirrel" in prompt
        assert "Magical forest" in prompt
        assert "Hazel" in prompt
        assert "watercolor" in prompt
        assert "5 page outlines" in prompt
        assert "Title" in prompt

    def test_build_story_planning_prompt_multiple_characters(self):
        """Test prompt with multiple characters."""
        inputs = GenerationInputs(
            audience_age=8,
            topic="Adventure",
            setting="Forest",
            format="storybook",
            illustration_style="digital",
            characters=["Alice", "Bob", "Charlie"],
            page_count=10
        )

        prompt = build_story_planning_prompt(inputs)

        assert "Alice, Bob, Charlie" in prompt
        assert "10 page outlines" in prompt

    def test_build_story_planning_prompt_no_characters(self):
        """Test prompt with no specific characters."""
        inputs = GenerationInputs(
            audience_age=6,
            topic="Mystery",
            setting="Castle",
            format="storybook",
            illustration_style="cartoon",
            characters=[],
            page_count=8
        )

        prompt = build_story_planning_prompt(inputs)

        assert "the main character" in prompt

    def test_get_age_guidelines_ages_3_4(self):
        """Test age guidelines for 3-4 year olds."""
        guidelines = _get_age_guidelines(4)

        assert "3-4" in guidelines
        assert "simple sentences" in guidelines.lower()
        assert "repetition" in guidelines.lower()

    def test_get_age_guidelines_ages_5_6(self):
        """Test age guidelines for 5-6 year olds."""
        guidelines = _get_age_guidelines(6)

        assert "5-6" in guidelines
        assert "cause and effect" in guidelines.lower()

    def test_get_age_guidelines_ages_7_8(self):
        """Test age guidelines for 7-8 year olds."""
        guidelines = _get_age_guidelines(8)

        assert "7-8" in guidelines
        assert "courage" in guidelines.lower()

    def test_get_age_guidelines_ages_9_10(self):
        """Test age guidelines for 9-10 year olds."""
        guidelines = _get_age_guidelines(10)

        assert "9-10" in guidelines
        assert "independence" in guidelines.lower()

    def test_get_age_guidelines_ages_11_12(self):
        """Test age guidelines for 11-12 year olds."""
        guidelines = _get_age_guidelines(12)

        assert "11-12" in guidelines
        assert "identity" in guidelines.lower()


class TestPageGenerationPrompts:
    """Tests for page generation prompt templates."""

    def test_build_page_generation_prompt_first_page(self):
        """Test page generation prompt for first page."""
        from app.models.storybook import StoryMetadata

        inputs = GenerationInputs(
            audience_age=7,
            topic="Adventure",
            setting="Forest",
            format="storybook",
            illustration_style="watercolor",
            characters=["Hero"],
            page_count=5
        )

        metadata = StoryMetadata(
            title="Test Story",
            character_descriptions=[
                CharacterDescription(
                    name="Hero",
                    physical_description="Tall and brave",
                    personality="Kind",
                    role="protagonist"
                )
            ],
            character_relations="Hero is alone",
            story_outline="Hero goes on adventure",
            page_outlines=["Page 1: Hero starts journey"],
            illustration_style_guide="Bright colors"
        )

        prompt = build_page_generation_prompt(
            page_number=1,
            page_outline="Hero starts journey",
            metadata=metadata,
            inputs=inputs
        )

        assert "Page 1" in prompt
        assert "Hero starts journey" in prompt
        assert "Tall and brave" in prompt
        assert "7 years old" in prompt

    def test_build_page_generation_prompt_with_previous_context(self):
        """Test page generation with previous page context."""
        from app.models.storybook import StoryMetadata

        inputs = GenerationInputs(
            audience_age=8,
            topic="Mystery",
            setting="Castle",
            format="storybook",
            illustration_style="digital",
            characters=[],
            page_count=3
        )

        metadata = StoryMetadata(
            title="Test Story",
            character_descriptions=[],
            character_relations="",
            story_outline="Story arc",
            page_outlines=["Page 1: Start", "Page 2: Middle"],
            illustration_style_guide="Style guide"
        )

        prompt = build_page_generation_prompt(
            page_number=2,
            page_outline="Page 2 outline",
            metadata=metadata,
            inputs=inputs
        )

        assert "Page 2" in prompt
        assert "Page 1: Start" in prompt


class TestValidationPrompts:
    """Tests for validation prompt templates."""

    @pytest.mark.skip(reason="Requires Beanie initialization - covered by integration tests")
    def test_build_validation_prompt(self):
        """Test story validation prompt generation."""
        from app.models.storybook import Page, Storybook, StoryMetadata

        storybook = Storybook(
            title="Test Story",
            generation_inputs=GenerationInputs(
                audience_age=7,
                topic="Adventure",
                setting="Forest",
                format="storybook",
                illustration_style="watercolor",
                characters=["Hero"],
                page_count=2
            ),
            metadata=StoryMetadata(
                title="Test Story",
                character_descriptions=[
                    CharacterDescription(
                        name="Hero",
                        physical_description="Tall",
                        personality="Brave",
                        role="protagonist"
                    )
                ],
                character_relations="Hero alone",
                story_outline="Adventure story",
                page_outlines=["Page 1", "Page 2"],
                illustration_style_guide="Watercolor style"
            ),
            status="generating"
        )

        storybook.pages = [
            Page(
                page_number=1,
                text="Once upon a time...",
                illustration_prompt="A forest scene",
                generation_attempts=1,
                validated=False
            ),
            Page(
                page_number=2,
                text="The hero walked...",
                illustration_prompt="Hero walking",
                generation_attempts=1,
                validated=False
            )
        ]

        prompt = build_validation_prompt(storybook)

        assert "Once upon a time" in prompt
        assert "The hero walked" in prompt
        assert "Hero" in prompt
        assert "7 years old" in prompt
