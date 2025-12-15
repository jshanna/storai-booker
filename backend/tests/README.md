# Backend Tests

This directory contains unit and integration tests for the StorAI-Booker backend API.

## Running Tests

### Prerequisites

1. Ensure MongoDB is running locally on port 27017
2. Install dependencies:
   ```bash
   cd backend
   poetry install
   ```

### Run All Tests

```bash
poetry run pytest
```

### Run with Coverage

```bash
poetry run pytest --cov=app --cov-report=html
```

### Run Specific Test Files

```bash
poetry run pytest tests/test_api_stories.py
poetry run pytest tests/test_api_settings.py
```

### Run Specific Tests

```bash
poetry run pytest tests/test_api_stories.py::test_generate_story
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_api_stories.py` - Tests for story API endpoints
- `test_api_settings.py` - Tests for settings API endpoints

## Test Coverage

The tests cover:

- **Story API**:
  - Story generation (POST /api/stories/generate)
  - Listing stories with pagination and filters (GET /api/stories)
  - Getting a specific story (GET /api/stories/{id})
  - Getting story status (GET /api/stories/{id}/status)
  - Deleting stories (DELETE /api/stories/{id})
  - Request validation and error handling

- **Settings API**:
  - Getting default settings (GET /api/settings)
  - Updating settings (PUT /api/settings)
  - Partial updates
  - Resetting to defaults (POST /api/settings/reset)

## Fixtures

- `client` - Async HTTP client for testing API endpoints
- `db_client` - MongoDB test client (auto-cleanup)
- `init_test_db` - Initialize Beanie with test database
- `sample_story_data` - Sample story data for testing
- `sample_settings_data` - Sample settings data for testing

## Notes

- Each test function has its own isolated database
- Test database (`test_storai_booker`) is automatically cleaned up after each test
- Tests use the real FastAPI app with test database configuration
