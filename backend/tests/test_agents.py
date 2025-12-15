"""Tests for story generation agents."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.storybook import (
    GenerationInputs,
    StoryMetadata,
    CharacterDescription,
    Page,
    Storybook,
)
from app.services.agents.coordinator import CoordinatorAgent
from app.services.agents.page_generator import PageGeneratorAgent
from app.services.agents.validator import ValidatorAgent
from app.services.llm.prompts.story_planning import StoryPlanningOutput
from app.services.llm.prompts.page_generation import PageGenerationOutput
from app.services.llm.prompts.validation import ValidationOutput, ValidationIssue


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider."""
    provider = MagicMock()
    provider.generate_structured = AsyncMock()
    return provider


@pytest.fixture
def sample_generation_inputs():
    """Sample generation inputs."""
    return GenerationInputs(
        audience_age=7,
        topic="A brave squirrel exploring a magical forest",
        setting="Enchanted forest with talking animals",
        format="storybook",
        illustration_style="watercolor",
        characters=["Hazel the squirrel"],
        page_count=3,
    )


@pytest.fixture
def sample_story_metadata():
    """Sample story metadata."""
    return StoryMetadata(
        character_descriptions=[
            CharacterDescription(
                name="Hazel",
                physical_description="A small brown squirrel with bright eyes",
                personality="Brave, curious, kind-hearted",
                role="protagonist"
            )
        ],
        character_relations="Hazel is the main character",
        story_outline="Beginning: Hazel discovers forest. Middle: Explores. End: Returns home.",
        page_outlines=[
            "Page 1: Hazel stands at forest edge",
            "Page 2: Hazel meets talking owl",
            "Page 3: Hazel returns home with stories",
        ],
        illustration_style_guide="Watercolor with soft edges and warm colors"
    )


class TestCoordinatorAgent:
    """Tests for CoordinatorAgent."""

    @pytest.fixture
    def coordinator(self, mock_llm_provider):
        """Create coordinator agent."""
        return CoordinatorAgent(mock_llm_provider)

    @pytest.mark.asyncio
    async def test_plan_story_success(self, coordinator, mock_llm_provider, sample_generation_inputs):
        """Test successful story planning."""
        # Mock LLM response
        mock_planning_output = StoryPlanningOutput(
            character_descriptions=[
                CharacterDescription(
                    name="Hazel",
                    physical_description="A small brown squirrel",
                    personality="Brave and curious",
                    role="protagonist"
                )
            ],
            character_relations="Hazel is alone",
            story_outline="A squirrel's adventure",
            page_outlines=["Page 1", "Page 2", "Page 3"],
            illustration_style_guide="Watercolor style"
        )
        mock_llm_provider.generate_structured.return_value = mock_planning_output

        result = await coordinator.plan_story(sample_generation_inputs)

        # Verify result
        assert isinstance(result, StoryMetadata)
        assert len(result.character_descriptions) == 1
        assert result.character_descriptions[0].name == "Hazel"
        assert len(result.page_outlines) == 3
        assert result.story_outline == "A squirrel's adventure"

        # Verify LLM was called correctly
        assert mock_llm_provider.generate_structured.called

    @pytest.mark.asyncio
    async def test_plan_story_adjusts_page_count(self, coordinator, mock_llm_provider, sample_generation_inputs):
        """Test that page count is adjusted if LLM returns wrong number."""
        # Mock LLM response with wrong page count
        mock_planning_output = StoryPlanningOutput(
            character_descriptions=[CharacterDescription(
                name="Test", physical_description="Test", personality="Test", role="Test"
            )],
            character_relations="Test",
            story_outline="Test",
            page_outlines=["Page 1"],  # Only 1 page instead of 3
            illustration_style_guide="Test"
        )
        mock_llm_provider.generate_structured.return_value = mock_planning_output

        result = await coordinator.plan_story(sample_generation_inputs)

        # Should have adjusted to 3 pages
        assert len(result.page_outlines) == 3
        assert result.page_outlines[0] == "Page 1"
        assert "Continue the story" in result.page_outlines[1]

    @pytest.mark.asyncio
    async def test_expand_characters_not_implemented(self, coordinator):
        """Test that expand_characters raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await coordinator.expand_characters(
                ["Character 1", "Character 2"],
                "Fantasy story"
            )


class TestPageGeneratorAgent:
    """Tests for PageGeneratorAgent."""

    @pytest.fixture
    def page_generator(self, mock_llm_provider):
        """Create page generator agent."""
        return PageGeneratorAgent(mock_llm_provider)

    @pytest.mark.asyncio
    async def test_generate_page_success(
        self,
        page_generator,
        mock_llm_provider,
        sample_generation_inputs,
        sample_story_metadata
    ):
        """Test successful page generation."""
        # Mock LLM response
        mock_page_output = PageGenerationOutput(
            page_text="Hazel stood at the edge of the magical forest.",
            illustration_prompt="A small brown squirrel standing at forest edge, watercolor style"
        )
        mock_llm_provider.generate_structured.return_value = mock_page_output

        result = await page_generator.generate_page(
            page_number=1,
            page_outline="Page 1: Hazel stands at forest edge",
            metadata=sample_story_metadata,
            inputs=sample_generation_inputs
        )

        # Verify result
        assert isinstance(result, Page)
        assert result.page_number == 1
        assert result.text == "Hazel stood at the edge of the magical forest."
        assert "watercolor" in result.illustration_prompt
        assert result.illustration_url is None
        assert result.generation_attempts == 1
        assert result.validated is False

    @pytest.mark.asyncio
    async def test_regenerate_page_success(
        self,
        page_generator,
        mock_llm_provider,
        sample_generation_inputs,
        sample_story_metadata
    ):
        """Test successful page regeneration."""
        # Original page
        original_page = Page(
            page_number=1,
            text="Original text",
            illustration_prompt="Original prompt",
            generation_attempts=1,
            validated=False
        )

        # Mock LLM response
        mock_page_output = PageGenerationOutput(
            page_text="Corrected text",
            illustration_prompt="Corrected prompt"
        )
        mock_llm_provider.generate_structured.return_value = mock_page_output

        result = await page_generator.regenerate_page(
            page=original_page,
            issue_description="Character name was inconsistent",
            metadata=sample_story_metadata,
            inputs=sample_generation_inputs
        )

        # Verify result
        assert isinstance(result, Page)
        assert result.page_number == 1
        assert result.text == "Corrected text"
        assert result.generation_attempts == 2  # Incremented
        assert result.validated is False

        # Verify prompt included feedback
        call_args = mock_llm_provider.generate_structured.call_args
        prompt = call_args[1]['prompt']
        assert "Previous Attempt Had Issues" in prompt
        assert "Character name was inconsistent" in prompt


class TestValidatorAgent:
    """Tests for ValidatorAgent."""

    @pytest.fixture
    def validator(self, mock_llm_provider):
        """Create validator agent."""
        return ValidatorAgent(mock_llm_provider)

    @pytest.fixture
    def sample_storybook(self, sample_generation_inputs, sample_story_metadata):
        """Create sample storybook."""
        storybook = Storybook(
            title="Test Story",
            generation_inputs=sample_generation_inputs,
            metadata=sample_story_metadata,
            status="generating"
        )
        storybook.pages = [
            Page(
                page_number=1,
                text="Page 1 text",
                illustration_prompt="Page 1 prompt",
                generation_attempts=1,
                validated=False
            ),
            Page(
                page_number=2,
                text="Page 2 text",
                illustration_prompt="Page 2 prompt",
                generation_attempts=1,
                validated=False
            ),
        ]
        return storybook

    @pytest.mark.asyncio
    async def test_validate_story_success(
        self,
        validator,
        mock_llm_provider,
        sample_storybook
    ):
        """Test successful story validation with no issues."""
        # Mock validation response
        mock_validation = ValidationOutput(
            is_valid=True,
            overall_quality="Excellent story with good flow",
            issues=[],
            suggestions=["Great work!"]
        )
        mock_llm_provider.generate_structured.return_value = mock_validation

        result = await validator.validate_story(sample_storybook)

        # Verify result
        assert isinstance(result, ValidationOutput)
        assert result.is_valid is True
        assert len(result.issues) == 0
        assert mock_llm_provider.generate_structured.called

    @pytest.mark.asyncio
    async def test_validate_story_with_issues(
        self,
        validator,
        mock_llm_provider,
        sample_storybook
    ):
        """Test validation with issues found."""
        # Mock validation response with issues
        mock_validation = ValidationOutput(
            is_valid=False,
            overall_quality="Has some inconsistencies",
            issues=[
                ValidationIssue(
                    page_number=1,
                    issue_type="character_inconsistency",
                    description="Character name spelled differently",
                    severity="critical"
                ),
                ValidationIssue(
                    page_number=2,
                    issue_type="narrative_flow",
                    description="Transition is abrupt",
                    severity="moderate"
                )
            ],
            suggestions=["Fix character name", "Improve transition"]
        )
        mock_llm_provider.generate_structured.return_value = mock_validation

        result = await validator.validate_story(sample_storybook)

        # Verify result
        assert result.is_valid is False
        assert len(result.issues) == 2
        assert result.issues[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_validate_page(
        self,
        validator,
        mock_llm_provider,
        sample_storybook
    ):
        """Test single page validation."""
        # Mock validation response
        mock_validation = ValidationOutput(
            is_valid=True,
            overall_quality="Good",
            issues=[],
            suggestions=[]
        )
        mock_llm_provider.generate_structured.return_value = mock_validation

        is_valid, issues = await validator.validate_page(sample_storybook, 1)

        # Verify result
        assert is_valid is True
        assert len(issues) == 0

    @pytest.mark.asyncio
    async def test_validate_page_with_issues(
        self,
        validator,
        mock_llm_provider,
        sample_storybook
    ):
        """Test single page validation with issues."""
        # Mock validation response
        mock_validation = ValidationOutput(
            is_valid=False,
            overall_quality="Issues found",
            issues=[
                ValidationIssue(
                    page_number=1,
                    issue_type="age_inappropriate",
                    description="Word too complex for age 7",
                    severity="moderate"
                )
            ],
            suggestions=["Simplify language"]
        )
        mock_llm_provider.generate_structured.return_value = mock_validation

        is_valid, issues = await validator.validate_page(sample_storybook, 1)

        # Verify result
        assert is_valid is False
        assert len(issues) == 1
        assert "Word too complex" in issues[0]

    def test_get_pages_needing_regeneration(self, validator):
        """Test extracting pages that need regeneration."""
        validation_output = ValidationOutput(
            is_valid=False,
            overall_quality="Issues found",
            issues=[
                ValidationIssue(
                    page_number=1,
                    issue_type="character_inconsistency",
                    description="Name wrong",
                    severity="critical"
                ),
                ValidationIssue(
                    page_number=1,
                    issue_type="narrative_flow",
                    description="Flow issue",
                    severity="moderate"
                ),
                ValidationIssue(
                    page_number=2,
                    issue_type="minor_typo",
                    description="Typo",
                    severity="minor"  # Should not be included
                ),
                ValidationIssue(
                    page_number=3,
                    issue_type="age_inappropriate",
                    description="Too complex",
                    severity="moderate"
                )
            ],
            suggestions=[]
        )

        result = validator.get_pages_needing_regeneration(validation_output)

        # Should only include pages 1 and 3 (moderate/critical issues)
        assert len(result) == 2
        page_numbers = [page_num for page_num, _ in result]
        assert 1 in page_numbers
        assert 3 in page_numbers
        assert 2 not in page_numbers  # Minor issue, excluded

        # Verify issue descriptions are combined for page 1
        page_1_issues = next(issues for page_num, issues in result if page_num == 1)
        assert "Name wrong" in page_1_issues
        assert "Flow issue" in page_1_issues
