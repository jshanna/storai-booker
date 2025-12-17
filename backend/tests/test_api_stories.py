"""Tests for story API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_generate_story(authenticated_client, sample_story_data):
    """Test story generation endpoint."""
    client, user = authenticated_client
    response = await client.post("/api/stories/generate", json=sample_story_data)

    assert response.status_code == 202
    data = response.json()
    assert data["title"] == sample_story_data["title"]
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_generate_story_requires_auth(client: AsyncClient, sample_story_data):
    """Test that story generation requires authentication."""
    response = await client.post("/api/stories/generate", json=sample_story_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_stories_empty(authenticated_client):
    """Test listing stories when database is empty."""
    client, user = authenticated_client
    response = await client.get("/api/stories")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["stories"] == []
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_stories_requires_auth(client: AsyncClient):
    """Test that listing stories requires authentication."""
    response = await client.get("/api/stories")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_stories_with_pagination(authenticated_client, sample_story_data):
    """Test listing stories with pagination."""
    client, user = authenticated_client

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
async def test_list_stories_with_filters(authenticated_client, sample_story_data):
    """Test listing stories with format filter."""
    client, user = authenticated_client

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
async def test_get_story(authenticated_client, sample_story_data):
    """Test getting a specific story."""
    client, user = authenticated_client

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
async def test_get_story_not_found(authenticated_client):
    """Test getting a non-existent story."""
    client, user = authenticated_client
    fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
    response = await client.get(f"/api/stories/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_story_invalid_id(authenticated_client):
    """Test getting a story with invalid ID format."""
    client, user = authenticated_client
    response = await client.get("/api/stories/invalid-id")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_story_status(authenticated_client, sample_story_data):
    """Test getting story generation status."""
    client, user = authenticated_client

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
async def test_delete_story(authenticated_client, sample_story_data):
    """Test deleting a story."""
    client, user = authenticated_client

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
async def test_validation_errors(authenticated_client):
    """Test request validation."""
    client, user = authenticated_client

    # Missing required fields
    response = await client.post("/api/stories/generate", json={})
    assert response.status_code == 422

    # Invalid age (below schema minimum of 0)
    invalid_data = {
        "title": "Test",
        "generation_inputs": {
            "audience_age": -1,  # Below schema minimum
            "topic": "Test",
            "setting": "Test",
            "format": "storybook",
            "illustration_style": "test",
            "page_count": 10,
        },
    }
    response = await client.post("/api/stories/generate", json=invalid_data)
    assert response.status_code == 422

    # Invalid page count (above maximum of 50)
    invalid_data = {
        "title": "Test",
        "generation_inputs": {
            "audience_age": 7,
            "topic": "Test",
            "setting": "Test",
            "format": "storybook",
            "illustration_style": "test",
            "page_count": 100,  # Above schema maximum
        },
    }
    response = await client.post("/api/stories/generate", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_age_range_enforcement(authenticated_client, sample_story_data):
    """Test that age range is enforced via settings."""
    client, user = authenticated_client

    # Enable age enforcement in settings
    await client.put("/api/settings", json={
        "age_range": {"min": 5, "max": 10, "enforce": True}
    })

    # Try to create story with age outside the allowed range
    story_data = sample_story_data.copy()
    story_data["generation_inputs"]["audience_age"] = 2  # Below min of 5
    response = await client.post("/api/stories/generate", json=story_data)
    assert response.status_code == 400
    # Check for error message in either 'detail' or 'message' field
    response_data = response.json()
    error_message = response_data.get("detail") or response_data.get("message") or str(response_data)
    assert "outside allowed range" in error_message.lower() or "2" in error_message


@pytest.mark.asyncio
async def test_user_can_only_see_own_stories(authenticated_client, client, auth_headers, sample_story_data):
    """Test that users can only see their own stories."""
    # Create story with first user
    client1, user1 = authenticated_client
    create_response = await client1.post("/api/stories/generate", json=sample_story_data)
    story_id = create_response.json()["id"]

    # Second user (from auth_headers fixture) should not see the story
    response = await client.get(f"/api/stories/{story_id}", headers=auth_headers)
    assert response.status_code == 404

    # Second user's list should be empty
    list_response = await client.get("/api/stories", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
