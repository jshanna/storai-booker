"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from app.models.storybook import Storybook
from app.models.settings import AppSettings


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_client():
    """Create a test database client."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    yield client
    # Cleanup: drop test database
    await client.drop_database("test_storai_booker")
    client.close()


@pytest.fixture(scope="function")
async def init_test_db(db_client):
    """Initialize Beanie with test database."""
    await init_beanie(
        database=db_client["test_storai_booker"],
        document_models=[Storybook, AppSettings],
    )


@pytest.fixture(scope="function")
async def client(init_test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
