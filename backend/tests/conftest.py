"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from app.models.storybook import Storybook
from app.models.settings import AppSettings
from app.models.user import User
from app.models.comment import Comment
from app.models.bookmark import Bookmark


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def init_test_db():
    """Initialize Beanie with test database."""
    # Create a new client for each test to avoid connection issues
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["test_storai_booker"]

    await init_beanie(
        database=database,
        document_models=[Storybook, AppSettings, User, Comment, Bookmark],
    )

    yield client

    # Cleanup: clear collections and close connection
    try:
        await Storybook.delete_all()
        await AppSettings.delete_all()
        await User.delete_all()
        await Comment.delete_all()
        await Bookmark.delete_all()
    except Exception:
        pass  # Ignore cleanup errors
    finally:
        client.close()


@pytest.fixture(scope="function")
async def client(init_test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_story_data():
    """Sample story data for testing."""
    return {
        "title": "Test Story",
        "generation_inputs": {
            "audience_age": 7,
            "topic": "A brave squirrel",
            "setting": "Enchanted forest",
            "format": "storybook",
            "illustration_style": "watercolor",
            "characters": ["Hazel the squirrel"],
            "page_count": 10,
        },
    }


@pytest.fixture
def sample_settings_data():
    """Sample settings data for testing."""
    return {
        "age_range": {"min": 5, "max": 12, "enforce": True},
        "primary_llm_provider": {
            "name": "openai",
            "api_key": "test-key",
            "text_model": "gpt-4-turbo-preview",
            "image_model": "dall-e-3",
        },
    }


@pytest.fixture
async def test_user(init_test_db):
    """Create a test user for authentication."""
    from app.services.auth import auth_service

    user = await auth_service.create_user(
        email="testuser@example.com",
        password="TestPass123",
        full_name="Test User",
    )
    return user


@pytest.fixture
async def auth_headers(test_user):
    """Get authentication headers for the test user."""
    from app.services.auth import auth_service

    tokens = auth_service.create_token_pair(test_user)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def authenticated_client(init_test_db) -> AsyncGenerator[tuple, None]:
    """Create a test client with an authenticated user and configured settings."""
    from app.services.auth import auth_service
    from app.models.settings import AppSettings, LLMProviderConfig

    # Create user
    user = await auth_service.create_user(
        email="authuser@example.com",
        password="TestPass123",
        full_name="Auth User",
    )

    # Create settings with a mock API key so story generation works
    settings = AppSettings(
        user_id=str(user.id),
        primary_llm_provider=LLMProviderConfig(
            name="google",
            api_key="test-api-key-for-testing",
            text_model="gemini-2.0-flash",
            image_model="gemini-2.0-flash-exp",
        ),
    )
    await settings.insert()

    # Get tokens
    tokens = auth_service.create_token_pair(user)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac, user
