"""Tests for story API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_story(client: AsyncClient, sample_story_data):
    """Test story generation endpoint."""
    response = await client.post("/api/stories/generate", json=sample_story_data)

    assert response.status_code == 202
    data = response.json()
    assert data["title"] == sample_story_data["title"]
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_stories_empty(client: AsyncClient):
    """Test listing stories when database is empty."""
    response = await client.get("/api/stories")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["stories"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_stories_with_pagination(client: AsyncClient, sample_story_data):
    """Test listing stories with pagination."""
    # Create multiple stories
    for i in range(15):
        story_data = sample_story_data.copy()
        story_data["title"] = f"Test Story {i}"
        await client.post("/api/stories/generate", json=story_data)

    # Test first page
    response = await client.get("/api/stories?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["stories"]) == 10
    assert data["page"] == 1

    # Test second page
    response = await client.get("/api/stories?page=2&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["stories"]) == 5
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_stories_with_filters(client: AsyncClient, sample_story_data):
    """Test listing stories with format filter."""
    # Create storybook
    storybook_data = sample_story_data.copy()
    storybook_data["generation_inputs"]["format"] = "storybook"
    await client.post("/api/stories/generate", json=storybook_data)

    # Create comic
    comic_data = sample_story_data.copy()
    comic_data["title"] = "Test Comic"
    comic_data["generation_inputs"]["format"] = "comic"
    comic_data["generation_inputs"]["panels_per_page"] = 4
    await client.post("/api/stories/generate", json=comic_data)

    # Filter by format
    response = await client.get("/api/stories?format=storybook")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["stories"][0]["generation_inputs"]["format"] == "storybook"


@pytest.mark.asyncio
async def test_get_story(client: AsyncClient, sample_story_data):
    """Test getting a specific story."""
    # Create story
    create_response = await client.post("/api/stories/generate", json=sample_story_data)
    story_id = create_response.json()["id"]

    # Get story
    response = await client.get(f"/api/stories/{story_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == story_id
    assert data["title"] == sample_story_data["title"]


@pytest.mark.asyncio
async def test_get_story_not_found(client: AsyncClient):
    """Test getting a non-existent story."""
    fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
    response = await client.get(f"/api/stories/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_story_invalid_id(client: AsyncClient):
    """Test getting a story with invalid ID format."""
    response = await client.get("/api/stories/invalid-id")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_story_status(client: AsyncClient, sample_story_data):
    """Test getting story generation status."""
    # Create story
    create_response = await client.post("/api/stories/generate", json=sample_story_data)
    story_id = create_response.json()["id"]

    # Get status
    response = await client.get(f"/api/stories/{story_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == story_id
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_delete_story(client: AsyncClient, sample_story_data):
    """Test deleting a story."""
    # Create story
    create_response = await client.post("/api/stories/generate", json=sample_story_data)
    story_id = create_response.json()["id"]

    # Delete story
    response = await client.delete(f"/api/stories/{story_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = await client.get(f"/api/stories/{story_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_validation_errors(client: AsyncClient):
    """Test request validation."""
    # Missing required fields
    response = await client.post("/api/stories/generate", json={})
    assert response.status_code == 422

    # Invalid age
    invalid_data = {
        "title": "Test",
        "generation_inputs": {
            "audience_age": 2,  # Too young (min is 3)
            "topic": "Test",
            "setting": "Test",
            "format": "storybook",
            "illustration_style": "test",
            "page_count": 10,
        },
    }
    response = await client.post("/api/stories/generate", json=invalid_data)
    assert response.status_code == 422
