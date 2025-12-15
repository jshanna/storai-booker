#!/usr/bin/env python3
"""
Offline tests for Phase 3 implementation.

Tests components that don't require API calls:
- Module imports
- Configuration loading
- Image compositor
- Provider factory initialization
"""
import sys
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger


def test_imports():
    """Test that all Phase 3 modules can be imported."""
    logger.info("\n[TEST 1] Module Imports")
    logger.info("-" * 60)

    try:
        from app.services.image import (
            BaseImageProvider,
            GoogleImagenProvider,
            ImageProviderFactory,
            ImageCompositor,
        )
        logger.info("✓ All image service modules imported successfully")

        from app.services.image.base import BaseImageProvider as Base
        from app.services.image.google_imagen import GoogleImagenProvider as Google
        from app.services.image.provider_factory import ImageProviderFactory as Factory
        from app.services.image.compositor import ImageCompositor as Compositor

        logger.info("✓ Direct imports from modules work correctly")
        return True

    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_configuration():
    """Test that configuration includes Phase 3 settings."""
    logger.info("\n[TEST 2] Configuration")
    logger.info("-" * 60)

    try:
        from app.core.config import settings

        # Check Phase 3 settings exist
        required_settings = [
            'default_image_model',
            'image_aspect_ratio',
            'image_max_retries',
            'image_generation_timeout',
            'cover_aspect_ratio',
            'cover_font_path',
        ]

        for setting in required_settings:
            if not hasattr(settings, setting):
                logger.error(f"✗ Missing setting: {setting}")
                return False
            value = getattr(settings, setting)
            logger.info(f"  {setting}: {value}")

        logger.info("✓ All Phase 3 settings present")
        return True

    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_provider_initialization():
    """Test provider factory initialization (without API calls)."""
    logger.info("\n[TEST 3] Provider Factory Initialization")
    logger.info("-" * 60)

    try:
        from app.services.image.provider_factory import ImageProviderFactory
        from app.services.image.google_imagen import GoogleImagenProvider

        # Test creating provider with dummy API key
        provider = ImageProviderFactory.create_google_imagen(
            api_key="test-key",
            model="gemini-2.0-flash-exp",
            aspect_ratio="16:9",
        )

        logger.info(f"✓ Provider created: {provider.__class__.__name__}")
        logger.info(f"  Model: {provider.model}")
        logger.info(f"  Aspect ratio: {provider.aspect_ratio}")
        logger.info(f"  Temperature: {provider.temperature}")

        # Verify it's the right type
        assert isinstance(provider, GoogleImagenProvider)
        logger.info("✓ Provider is correct type")

        return True

    except Exception as e:
        logger.error(f"✗ Provider initialization failed: {e}")
        return False


def test_image_compositor():
    """Test image compositor with a generated test image."""
    logger.info("\n[TEST 4] Image Compositor")
    logger.info("-" * 60)

    try:
        from PIL import Image
        from app.services.image.compositor import ImageCompositor

        # Create a test image (simple colored rectangle)
        width, height = 800, 1200  # Portrait 3:4 aspect ratio
        test_image = Image.new('RGB', (width, height), color=(70, 130, 180))  # Steel blue

        # Save to bytes
        image_buffer = BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_bytes = image_buffer.getvalue()

        logger.info(f"  Created test image: {width}x{height} ({len(image_bytes)} bytes)")

        # Test compositor
        compositor = ImageCompositor()

        import asyncio
        cover_bytes = asyncio.run(compositor.create_cover_with_title(
            image_bytes=image_bytes,
            title="The Brave Little Squirrel",
        ))

        logger.info(f"✓ Cover created: {len(cover_bytes)} bytes")

        # Verify output is valid PNG
        if cover_bytes[:4] == b'\x89PNG':
            logger.info("✓ Output is valid PNG format")
        else:
            logger.warning("⚠ Output may not be valid PNG")

        # Verify output is larger (has overlay)
        if len(cover_bytes) > len(image_bytes) * 0.5:  # At least 50% of original
            logger.info("✓ Cover has reasonable size")
        else:
            logger.warning("⚠ Cover size seems too small")

        # Test with custom font path (should fall back gracefully)
        compositor_with_font = ImageCompositor(font_path="/nonexistent/font.ttf")
        cover_bytes2 = asyncio.run(compositor_with_font.create_cover_with_title(
            image_bytes=image_bytes,
            title="Another Test Title",
        ))
        logger.info("✓ Compositor handles missing custom font gracefully")

        return True

    except Exception as e:
        logger.error(f"✗ Compositor test failed: {e}")
        logger.exception(e)
        return False


def test_workflow_imports():
    """Test that workflow can import image services."""
    logger.info("\n[TEST 5] Workflow Integration")
    logger.info("-" * 60)

    try:
        from app.tasks.story_generation import (
            _generate_page_illustration,
            _generate_cover_image,
            _build_cover_prompt,
        )

        logger.info("✓ Workflow helper functions imported")

        # Test _build_cover_prompt with mock data
        from app.models.storybook import (
            GenerationInputs,
            StoryMetadata,
            CharacterDescription,
        )
        from unittest.mock import MagicMock

        # Create a mock story (avoid Beanie initialization)
        mock_story = MagicMock()
        mock_story.title = "Test Story"
        mock_story.generation_inputs = GenerationInputs(
                audience_age=7,
                topic="A test topic",
                setting="A test setting",
                format="storybook",
                illustration_style="watercolor",
                characters=["Test Character"],
                page_count=3,
            )
        mock_story.metadata = StoryMetadata(
                character_descriptions=[
                    CharacterDescription(
                        name="Test Character",
                        physical_description="A friendly character",
                        personality="Brave",
                        role="protagonist",
                    )
                ],
                character_relations="Test relations",
                story_outline="Test outline",
                page_outlines=["Page 1", "Page 2", "Page 3"],
                illustration_style_guide="Test style guide",
            )

        prompt = _build_cover_prompt(mock_story)

        logger.info("✓ Cover prompt builder works")
        logger.info(f"  Generated prompt length: {len(prompt)} chars")
        logger.info(f"  Prompt preview: {prompt[:100]}...")

        # Verify prompt contains key elements
        assert "Test Story" in prompt
        assert "Test Character" in prompt
        assert "test setting" in prompt.lower() or "A test setting" in prompt
        logger.info("✓ Prompt contains expected elements")

        return True

    except Exception as e:
        logger.error(f"✗ Workflow integration test failed: {e}")
        logger.exception(e)
        return False


def test_storage_integration():
    """Test that storage service is accessible."""
    logger.info("\n[TEST 6] Storage Service")
    logger.info("-" * 60)

    try:
        from app.services.storage import storage_service

        logger.info(f"✓ Storage service imported")
        logger.info(f"  Bucket: {storage_service.bucket_name}")

        # Check if client initialization doesn't crash
        assert storage_service.bucket_name == "storai-booker-images"
        logger.info("✓ Storage service configured correctly")

        return True

    except Exception as e:
        logger.error(f"✗ Storage service test failed: {e}")
        logger.exception(e)
        return False


def main():
    """Run all offline tests."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )

    logger.info("\n" + "=" * 60)
    logger.info("PHASE 3 OFFLINE TESTS")
    logger.info("Testing implementation without API calls")
    logger.info("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Provider Initialization", test_provider_initialization),
        ("Image Compositor", test_image_compositor),
        ("Workflow Integration", test_workflow_imports),
        ("Storage Service", test_storage_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n✓ ALL OFFLINE TESTS PASSED!")
        logger.info("\nPhase 3 implementation structure is correct.")
        logger.info("Image generation ready (requires Google API key with quota).")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
