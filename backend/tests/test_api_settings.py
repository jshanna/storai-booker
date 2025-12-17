"""Tests for settings API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_settings_default(authenticated_client):
    """Test getting default settings."""
    client, user = authenticated_client
    response = await client.get("/api/settings")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert "age_range" in data
    assert "content_filters" in data
    assert "generation_limits" in data
    assert "primary_llm_provider" in data


@pytest.mark.asyncio
async def test_get_settings_requires_auth(client: AsyncClient):
    """Test that getting settings requires authentication."""
    response = await client.get("/api/settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_settings(authenticated_client, sample_settings_data):
    """Test updating settings."""
    client, user = authenticated_client
    response = await client.put("/api/settings", json=sample_settings_data)

    assert response.status_code == 200
    data = response.json()
    assert data["age_range"]["min"] == 5
    assert data["age_range"]["max"] == 12
    assert data["primary_llm_provider"]["name"] == "openai"


@pytest.mark.asyncio
async def test_update_settings_requires_auth(client: AsyncClient, sample_settings_data):
    """Test that updating settings requires authentication."""
    response = await client.put("/api/settings", json=sample_settings_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_settings_partial(authenticated_client):
    """Test partial settings update."""
    client, user = authenticated_client

    # Update only age range
    update_data = {
        "age_range": {"min": 6, "max": 10, "enforce": True}
    }
    response = await client.put("/api/settings", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["age_range"]["min"] == 6
    assert data["age_range"]["max"] == 10


@pytest.mark.asyncio
async def test_reset_settings(authenticated_client, sample_settings_data):
    """Test resetting settings to defaults."""
    client, user = authenticated_client

    # First update settings
    await client.put("/api/settings", json=sample_settings_data)

    # Reset settings
    response = await client.post("/api/settings/reset")

    assert response.status_code == 200
    data = response.json()
    # Verify defaults
    assert data["age_range"]["min"] == 3
    assert data["age_range"]["max"] == 12
    assert data["primary_llm_provider"]["name"] == "openai"


@pytest.mark.asyncio
async def test_reset_settings_requires_auth(client: AsyncClient):
    """Test that resetting settings requires authentication."""
    response = await client.post("/api/settings/reset")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_settings_are_isolated(authenticated_client, client, auth_headers, sample_settings_data):
    """Test that each user has their own settings."""
    client1, user1 = authenticated_client

    # First user updates settings
    await client1.put("/api/settings", json=sample_settings_data)

    # Verify first user's settings are updated
    response1 = await client1.get("/api/settings")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["age_range"]["min"] == 5

    # Second user should have default settings
    response2 = await client.get("/api/settings", headers=auth_headers)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["age_range"]["min"] == 3  # Default value
