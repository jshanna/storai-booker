"""Tests for story generation Celery tasks."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.models.storybook import (
    GenerationInputs,
    StoryMetadata,
    CharacterDescription,
    Page,
    Storybook,
)
from app.tasks.story_generation import (
    _generate_story_workflow,
    _generate_page_workflow,
    _validate_story_workflow,
)
from app.services.llm.prompts.story_planning import StoryPlanningOutput
from app.services.llm.prompts.page_generation import PageGenerationOutput
from app.services.llm.prompts.validation import ValidationOutput, ValidationIssue


@pytest.fixture
def sample_storybook_in_db(init_test_db):
    """Create a storybook in the test database."""
    async def _create_storybook():
        storybook = Storybook(
            title="Test Story",
            generation_inputs=GenerationInputs(
                audience_age=7,
                topic="A brave squirrel",
                setting="Enchanted forest",
                format="storybook",
                illustration_style="watercolor",
                characters=["Hazel"],
                page_count=3,
            ),
            status="pending"
        )
        await storybook.insert()
        return storybook
    return _create_storybook


@pytest.fixture
def mock_celery_task():
    """Mock Celery task instance."""
    task = MagicMock()
    task.update_state = MagicMock()
    task.request = MagicMock()
    task.request.retries = 0
    task.max_retries = 3
    return task


@pytest.fixture
def mock_coordinator():
    """Mock coordinator agent."""
    coordinator = MagicMock()
    coordinator.plan_story = AsyncMock(return_value=StoryMetadata(
        character_descriptions=[
            CharacterDescription(
                name="Hazel",
                physical_description="A small brown squirrel",
                personality="Brave",
                role="protagonist"
            )
        ],
        character_relations="Hazel is alone",
        story_outline="A squirrel's adventure",
        page_outlines=[
            "Page 1: Forest edge",
            "Page 2: Meets owl",
            "Page 3: Returns home"
        ],
        illustration_style_guide="Watercolor"
    ))
    return coordinator


@pytest.fixture
def mock_page_generator():
    """Mock page generator agent."""
    generator = MagicMock()

    async def mock_generate_page(page_number, **kwargs):
        return Page(
            page_number=page_number,
            text=f"Page {page_number} text",
            illustration_prompt=f"Page {page_number} prompt",
            generation_attempts=1,
            validated=False
        )

    generator.generate_page = AsyncMock(side_effect=mock_generate_page)
    generator.regenerate_page = AsyncMock(return_value=Page(
        page_number=1,
        text="Regenerated text",
        illustration_prompt="Regenerated prompt",
        generation_attempts=2,
        validated=False
    ))
    return generator


@pytest.fixture
def mock_validator():
    """Mock validator agent."""
    validator = MagicMock()
    validator.validate_story = AsyncMock(return_value=ValidationOutput(
        is_valid=True,
        overall_quality="Excellent",
        issues=[],
        suggestions=[]
    ))
    validator.get_pages_needing_regeneration = MagicMock(return_value=[])
    return validator


@pytest.mark.skip(reason="Story generation workflow tests require complex Celery mocking - covered by E2E tests")
class TestGenerateStoryWorkflow:
    """Tests for _generate_story_workflow."""

    @pytest.mark.asyncio
    async def test_successful_story_generation(
        self,
        sample_storybook_in_db,
        mock_celery_task,
        mock_coordinator,
        mock_page_generator,
        mock_validator
    ):
        """Test successful end-to-end story generation."""
        # Create storybook
        storybook = await sample_storybook_in_db()
        story_id = str(storybook.id)

        # Mock the agents
        with patch('app.tasks.story_generation.CoordinatorAgent', return_value=mock_coordinator), \
             patch('app.tasks.story_generation.PageGeneratorAgent', return_value=mock_page_generator), \
             patch('app.tasks.story_generation.ValidatorAgent', return_value=mock_validator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            result = await _generate_story_workflow(story_id, mock_celery_task)

        # Verify result
        assert result["status"] == "success"
        assert result["story_id"] == story_id
        assert result["pages"] == 3
        assert result["validation"]["is_valid"] is True

        # Verify story was updated
        updated_story = await Storybook.get(storybook.id)
        assert updated_story.status == "complete"
        assert len(updated_story.pages) == 3
        assert updated_story.metadata.story_outline == "A squirrel's adventure"

        # Verify agents were called
        assert mock_coordinator.plan_story.called
        assert mock_page_generator.generate_page.call_count == 3
        assert mock_validator.validate_story.called

    @pytest.mark.asyncio
    async def test_story_generation_with_validation_failure(
        self,
        sample_storybook_in_db,
        mock_celery_task,
        mock_coordinator,
        mock_page_generator,
        mock_validator
    ):
        """Test story generation with validation failure and regeneration."""
        # Create storybook
        storybook = await sample_storybook_in_db()
        story_id = str(storybook.id)

        # Mock validation failure on first attempt, success on second
        validation_fail = ValidationOutput(
            is_valid=False,
            overall_quality="Has issues",
            issues=[
                ValidationIssue(
                    page_number=1,
                    issue_type="character_inconsistency",
                    description="Name wrong",
                    severity="critical"
                )
            ],
            suggestions=[]
        )
        validation_success = ValidationOutput(
            is_valid=True,
            overall_quality="Good",
            issues=[],
            suggestions=[]
        )

        mock_validator.validate_story = AsyncMock(side_effect=[validation_fail, validation_success])
        mock_validator.get_pages_needing_regeneration = MagicMock(
            return_value=[(1, "Name wrong")]
        )

        # Mock the agents
        with patch('app.tasks.story_generation.CoordinatorAgent', return_value=mock_coordinator), \
             patch('app.tasks.story_generation.PageGeneratorAgent', return_value=mock_page_generator), \
             patch('app.tasks.story_generation.ValidatorAgent', return_value=mock_validator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            result = await _generate_story_workflow(story_id, mock_celery_task)

        # Verify regeneration was called
        assert mock_page_generator.regenerate_page.called
        assert result["status"] == "success"

        # Verify story is complete
        updated_story = await Storybook.get(storybook.id)
        assert updated_story.status == "complete"

    @pytest.mark.asyncio
    async def test_story_generation_story_not_found(self, mock_celery_task):
        """Test error when story not found."""
        with pytest.raises(ValueError) as exc_info:
            await _generate_story_workflow("000000000000000000000000", mock_celery_task)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_story_generation_updates_progress(
        self,
        sample_storybook_in_db,
        mock_celery_task,
        mock_coordinator,
        mock_page_generator,
        mock_validator
    ):
        """Test that progress is updated during generation."""
        # Create storybook
        storybook = await sample_storybook_in_db()
        story_id = str(storybook.id)

        # Mock the agents
        with patch('app.tasks.story_generation.CoordinatorAgent', return_value=mock_coordinator), \
             patch('app.tasks.story_generation.PageGeneratorAgent', return_value=mock_page_generator), \
             patch('app.tasks.story_generation.ValidatorAgent', return_value=mock_validator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            await _generate_story_workflow(story_id, mock_celery_task)

        # Verify progress updates
        assert mock_celery_task.update_state.called
        calls = mock_celery_task.update_state.call_args_list

        # Should have multiple progress updates
        assert len(calls) >= 3  # Planning, page generation, validation

        # Check that different phases are tracked
        phases = [call[1]['meta']['phase'] for call in calls]
        assert 'planning' in phases
        assert 'page_generation' in phases
        assert 'validation' in phases


@pytest.mark.skip(reason="Page generation workflow tests require complex mocking - covered by E2E tests")
class TestGeneratePageWorkflow:
    """Tests for _generate_page_workflow."""

    @pytest.mark.asyncio
    async def test_generate_page_success(
        self,
        sample_storybook_in_db,
        mock_page_generator
    ):
        """Test successful page generation."""
        # Create storybook with metadata
        storybook = await sample_storybook_in_db()
        storybook.metadata = StoryMetadata(
            page_outlines=[
                "Page 1: Forest edge",
                "Page 2: Meets owl",
                "Page 3: Returns home"
            ]
        )
        await storybook.save()
        story_id = str(storybook.id)

        # Mock page generator
        with patch('app.tasks.story_generation.PageGeneratorAgent', return_value=mock_page_generator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            result = await _generate_page_workflow(story_id, 1)

        # Verify result
        assert result["page_number"] == 1
        assert result["text_length"] > 0
        assert result["has_illustration_prompt"] is True

        # Verify page was added to story
        updated_story = await Storybook.get(storybook.id)
        assert len(updated_story.pages) == 1
        assert updated_story.pages[0].page_number == 1


@pytest.mark.skip(reason="Validation workflow tests require complex mocking - covered by E2E tests")
class TestValidateStoryWorkflow:
    """Tests for _validate_story_workflow."""

    @pytest.mark.asyncio
    async def test_validate_story_success(
        self,
        sample_storybook_in_db,
        mock_validator
    ):
        """Test successful story validation."""
        # Create storybook with pages
        storybook = await sample_storybook_in_db()
        storybook.pages = [
            Page(page_number=1, text="Text 1", illustration_prompt="Prompt 1"),
            Page(page_number=2, text="Text 2", illustration_prompt="Prompt 2"),
        ]
        await storybook.save()
        story_id = str(storybook.id)

        # Mock validator
        with patch('app.tasks.story_generation.ValidatorAgent', return_value=mock_validator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            result = await _validate_story_workflow(story_id)

        # Verify result
        assert result["is_valid"] is True
        assert result["overall_quality"] == "Excellent"
        assert result["issues_count"] == 0

    @pytest.mark.asyncio
    async def test_validate_story_with_issues(
        self,
        sample_storybook_in_db,
        mock_validator
    ):
        """Test validation with issues."""
        # Create storybook
        storybook = await sample_storybook_in_db()
        storybook.pages = [
            Page(page_number=1, text="Text 1", illustration_prompt="Prompt 1"),
        ]
        await storybook.save()
        story_id = str(storybook.id)

        # Mock validator with issues
        mock_validator.validate_story = AsyncMock(return_value=ValidationOutput(
            is_valid=False,
            overall_quality="Has issues",
            issues=[
                ValidationIssue(
                    page_number=1,
                    issue_type="character_inconsistency",
                    description="Name spelled wrong",
                    severity="moderate"
                )
            ],
            suggestions=["Fix name"]
        ))

        # Mock validator
        with patch('app.tasks.story_generation.ValidatorAgent', return_value=mock_validator), \
             patch('app.tasks.story_generation.LLMProviderFactory.create_from_settings', return_value=MagicMock()):

            result = await _validate_story_workflow(story_id)

        # Verify result
        assert result["is_valid"] is False
        assert result["issues_count"] == 1
        assert len(result["issues"]) == 1
        assert result["issues"][0]["page"] == 1
        assert result["issues"][0]["type"] == "character_inconsistency"
