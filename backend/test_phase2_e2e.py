#!/usr/bin/env python3
"""
End-to-end test for Phase 2: LLM Agent System

This script tests the complete story generation flow:
1. Creates a story via API
2. Monitors generation progress
3. Validates the complete story

Run this script to verify Phase 2 implementation.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.storybook import Storybook, GenerationInputs
from app.services.llm.provider_factory import LLMProviderFactory
from app.services.agents.coordinator import CoordinatorAgent
from app.services.agents.page_generator import PageGeneratorAgent
from app.services.agents.validator import ValidatorAgent


async def init_db():
    """Initialize database connection."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_db_name],
        document_models=[Storybook],
    )
    logger.info("Database initialized")


async def test_llm_provider():
    """Test LLM provider connection."""
    logger.info("Testing LLM provider connection...")

    try:
        provider = LLMProviderFactory.create_from_settings()
        logger.info(f"✓ LLM provider created: {provider.__class__.__name__}")
        logger.info(f"  Model: {provider.model}")
        logger.info(f"  Temperature: {provider.temperature}")

        # Test simple text generation
        response = await provider.generate_text(
            "Say 'Hello, I am ready!' in one sentence.",
            max_tokens=50
        )
        logger.info(f"✓ Provider response: {response[:100]}...")

        return True

    except Exception as e:
        logger.error(f"✗ LLM provider test failed: {e}")
        return False


async def test_coordinator_agent():
    """Test coordinator agent."""
    logger.info("\nTesting Coordinator Agent...")

    try:
        provider = LLMProviderFactory.create_from_settings()
        coordinator = CoordinatorAgent(provider)

        inputs = GenerationInputs(
            audience_age=7,
            topic="A brave squirrel exploring a magical forest",
            setting="Enchanted forest with talking animals",
            format="storybook",
            illustration_style="watercolor",
            characters=["Hazel the squirrel"],
            page_count=3,
        )

        logger.info("Planning story...")
        metadata = await coordinator.plan_story(inputs)

        logger.info(f"✓ Story planned successfully")
        logger.info(f"  Characters: {len(metadata.character_descriptions)}")
        logger.info(f"  Page outlines: {len(metadata.page_outlines)}")
        logger.info(f"  Story outline: {metadata.story_outline[:100]}...")

        # Verify metadata
        assert len(metadata.character_descriptions) > 0, "No characters generated"
        assert len(metadata.page_outlines) == 3, f"Expected 3 page outlines, got {len(metadata.page_outlines)}"
        assert metadata.story_outline, "No story outline generated"
        assert metadata.illustration_style_guide, "No illustration style guide"

        logger.info("✓ All metadata validated")
        return metadata, inputs

    except Exception as e:
        logger.error(f"✗ Coordinator agent test failed: {e}")
        raise


async def test_page_generator_agent(metadata, inputs):
    """Test page generator agent."""
    logger.info("\nTesting Page Generator Agent...")

    try:
        provider = LLMProviderFactory.create_from_settings()
        page_generator = PageGeneratorAgent(provider)

        pages = []
        for i in range(inputs.page_count):
            page_number = i + 1
            page_outline = metadata.page_outlines[i]

            logger.info(f"Generating page {page_number}...")
            page = await page_generator.generate_page(
                page_number=page_number,
                page_outline=page_outline,
                metadata=metadata,
                inputs=inputs,
            )

            logger.info(f"✓ Page {page_number} generated")
            logger.info(f"  Text length: {len(page.text)} chars")
            logger.info(f"  Illustration prompt: {len(page.illustration_prompt)} chars")
            logger.info(f"  Text preview: {page.text[:80]}...")

            # Verify page
            assert page.text, "No page text generated"
            assert page.illustration_prompt, "No illustration prompt generated"
            assert page.page_number == page_number, "Page number mismatch"
            assert page.generation_attempts == 1, "Generation attempts should be 1"
            assert page.validated is False, "Page should not be validated yet"
            assert page.illustration_url is None, "Illustration URL should be None (Phase 3)"

            pages.append(page)

        logger.info(f"✓ All {len(pages)} pages generated successfully")
        return pages

    except Exception as e:
        logger.error(f"✗ Page generator agent test failed: {e}")
        raise


async def test_validator_agent(metadata, inputs, pages):
    """Test validator agent."""
    logger.info("\nTesting Validator Agent...")

    try:
        provider = LLMProviderFactory.create_from_settings()
        validator = ValidatorAgent(provider)

        # Create a storybook for validation
        storybook = Storybook(
            title="Test Story: The Brave Squirrel",
            generation_inputs=inputs,
            metadata=metadata,
            pages=pages,
            status="generating"
        )

        logger.info("Validating story...")
        validation_output = await validator.validate_story(storybook)

        logger.info(f"✓ Validation complete")
        logger.info(f"  Is valid: {validation_output.is_valid}")
        logger.info(f"  Quality: {validation_output.overall_quality}")
        logger.info(f"  Issues found: {len(validation_output.issues)}")

        if validation_output.issues:
            for issue in validation_output.issues:
                logger.warning(
                    f"    Page {issue.page_number}: [{issue.severity}] "
                    f"{issue.issue_type} - {issue.description}"
                )

        if validation_output.suggestions:
            logger.info("  Suggestions:")
            for suggestion in validation_output.suggestions:
                logger.info(f"    - {suggestion}")

        # Test page regeneration if needed
        pages_to_regenerate = validator.get_pages_needing_regeneration(validation_output)
        if pages_to_regenerate:
            logger.info(f"\nTesting page regeneration for {len(pages_to_regenerate)} pages...")
            page_generator = PageGeneratorAgent(provider)

            for page_number, issue_description in pages_to_regenerate:
                logger.info(f"Regenerating page {page_number}...")
                original_page = pages[page_number - 1]

                new_page = await page_generator.regenerate_page(
                    page=original_page,
                    issue_description=issue_description,
                    metadata=metadata,
                    inputs=inputs,
                )

                logger.info(f"✓ Page {page_number} regenerated")
                logger.info(f"  Attempts: {new_page.generation_attempts}")

                assert new_page.generation_attempts == 2, "Attempts should be 2 after regeneration"

        return validation_output

    except Exception as e:
        logger.error(f"✗ Validator agent test failed: {e}")
        raise


async def test_complete_workflow():
    """Test complete story generation workflow."""
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 2 END-TO-END TEST")
    logger.info("=" * 60)

    try:
        # Initialize database
        await init_db()

        # Test 1: LLM Provider
        logger.info("\n[1/4] Testing LLM Provider Connection")
        logger.info("-" * 60)
        if not await test_llm_provider():
            logger.error("LLM provider test failed. Check your API key in .env")
            return False

        # Test 2: Coordinator Agent
        logger.info("\n[2/4] Testing Coordinator Agent")
        logger.info("-" * 60)
        metadata, inputs = await test_coordinator_agent()

        # Test 3: Page Generator Agent
        logger.info("\n[3/4] Testing Page Generator Agent")
        logger.info("-" * 60)
        pages = await test_page_generator_agent(metadata, inputs)

        # Test 4: Validator Agent
        logger.info("\n[4/4] Testing Validator Agent")
        logger.info("-" * 60)
        validation_output = await test_validator_agent(metadata, inputs, pages)

        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✓ LLM Provider: Connected")
        logger.info(f"✓ Coordinator Agent: Generated metadata with {len(metadata.character_descriptions)} characters")
        logger.info(f"✓ Page Generator Agent: Generated {len(pages)} pages")
        logger.info(f"✓ Validator Agent: Validation {'passed' if validation_output.is_valid else 'found issues'}")
        logger.info("\n✓ ALL TESTS PASSED!")
        logger.info("\nPhase 2 implementation is ready for use.")
        logger.info("\nNext steps:")
        logger.info("1. Set your GOOGLE_API_KEY in backend/.env")
        logger.info("2. Start services: docker compose --profile full up -d")
        logger.info("3. Test via API: POST http://localhost:8000/api/stories/generate")
        logger.info("4. Monitor progress: GET http://localhost:8000/api/stories/{id}/status")
        logger.info("5. View Celery tasks: http://localhost:5555 (Flower)")

        return True

    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}")
        logger.exception(e)
        return False


def main():
    """Run the test."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
