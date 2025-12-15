"""Tests for settings API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_settings_default(client: AsyncClient):
    """Test getting default settings."""
    response = await client.get("/api/settings")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "default"
    assert "age_range" in data
    assert "content_filters" in data
    assert "generation_limits" in data
    assert "primary_llm_provider" in data


@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient, sample_settings_data):
    """Test updating settings."""
    response = await client.put("/api/settings", json=sample_settings_data)

    assert response.status_code == 200
    data = response.json()
    assert data["age_range"]["min"] == 5
    assert data["age_range"]["max"] == 12
    assert data["primary_llm_provider"]["name"] == "openai"


@pytest.mark.asyncio
async def test_update_settings_partial(client: AsyncClient):
    """Test partial settings update."""
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
async def test_reset_settings(client: AsyncClient, sample_settings_data):
    """Test resetting settings to defaults."""
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
