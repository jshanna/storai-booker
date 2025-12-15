# Phase 1 Local Testing Guide

## Prerequisites

Ensure Docker has proper permissions. Choose one:

**Option 1: Add your user to docker group (recommended)**
```bash
sudo usermod -aG docker $USER
newgrp docker  # Or log out and back in
```

**Option 2: Use sudo**
```bash
sudo docker compose up -d
```

## Step 1: Start Backend Services

```bash
# Start MongoDB, Redis, and MinIO
docker compose up -d

# Verify services are running
docker compose ps

# Expected output:
# - mongodb (port 27017)
# - redis (port 6379)
# - minio (ports 9000, 9001)
```

## Step 2: Set Up Backend Environment

```bash
cd backend

# Install Poetry if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Create .env file from example
cp .env.example .env

# Edit .env if needed (defaults should work with docker-compose)
```

## Step 3: Start FastAPI Server

```bash
# From backend directory
poetry run python main.py

# Server should start on http://localhost:8000
```

## Step 4: Test API Endpoints

### Health Check
```bash
curl http://localhost:8000/health

# Expected:
# {
#   "status": "healthy",
#   "app": "StorAI-Booker",
#   "version": "0.1.0",
#   "environment": "development",
#   "services": {
#     "database": "healthy",
#     "storage": "healthy"
#   }
# }
```

### API Documentation
Open in browser:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Test Story Generation

**Create a story:**
```bash
curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Magical Forest Adventure",
    "generation_inputs": {
      "audience_age": 7,
      "topic": "A brave squirrel exploring a magical forest",
      "setting": "Enchanted forest with talking animals",
      "format": "storybook",
      "illustration_style": "watercolor",
      "characters": ["Hazel the squirrel"],
      "page_count": 10
    }
  }'

# Save the returned "id" for next commands
```

**List stories:**
```bash
curl http://localhost:8000/api/stories
```

**Get specific story:**
```bash
curl http://localhost:8000/api/stories/{story_id}
```

**Get story status:**
```bash
curl http://localhost:8000/api/stories/{story_id}/status
```

**Delete story:**
```bash
curl -X DELETE http://localhost:8000/api/stories/{story_id}
```

### Test Settings API

**Get settings:**
```bash
curl http://localhost:8000/api/settings
```

**Update settings:**
```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "age_range": {
      "min": 5,
      "max": 12,
      "enforce": true
    },
    "primary_llm_provider": {
      "name": "openai",
      "api_key": "your-api-key-here",
      "text_model": "gpt-4-turbo-preview",
      "image_model": "dall-e-3"
    }
  }'
```

**Reset settings:**
```bash
curl -X POST http://localhost:8000/api/settings/reset
```

## Step 5: Run Unit Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test files
poetry run pytest tests/test_api_stories.py
poetry run pytest tests/test_api_settings.py

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Testing Filters and Pagination

**Filter by format:**
```bash
curl "http://localhost:8000/api/stories?format=storybook"
curl "http://localhost:8000/api/stories?format=comic"
```

**Filter by status:**
```bash
curl "http://localhost:8000/api/stories?status=pending"
curl "http://localhost:8000/api/stories?status=complete"
```

**Pagination:**
```bash
curl "http://localhost:8000/api/stories?page=1&page_size=5"
curl "http://localhost:8000/api/stories?page=2&page_size=5"
```

**Search:**
```bash
curl "http://localhost:8000/api/stories?search=magical"
```

## Testing Error Handling

**Invalid story ID:**
```bash
curl http://localhost:8000/api/stories/invalid-id
# Expected: 400 Bad Request
```

**Missing required fields:**
```bash
curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{}'
# Expected: 422 Validation Error
```

**Invalid age (too young):**
```bash
curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "generation_inputs": {
      "audience_age": 2,
      "topic": "Test",
      "setting": "Test",
      "format": "storybook",
      "illustration_style": "test",
      "page_count": 10
    }
  }'
# Expected: 422 Validation Error (min age is 3)
```

## Cleanup

```bash
# Stop services
docker compose down

# Remove volumes (deletes all data)
docker compose down -v
```

## Troubleshooting

### Services not starting
```bash
# Check logs
docker compose logs mongodb
docker compose logs redis
docker compose logs minio

# Restart specific service
docker compose restart mongodb
```

### Port already in use
```bash
# Check what's using the port
sudo ss -tulpn | grep :8000
sudo ss -tulpn | grep :27017

# Kill the process or change port in .env
```

### Database connection issues
```bash
# Verify MongoDB is accessible
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check backend logs for connection errors
```

## What's Working

After successful testing, you should have verified:

✅ Health check endpoint with service status
✅ Story CRUD operations (create, read, list, delete)
✅ Story listing with pagination and filters
✅ Settings CRUD operations
✅ Request validation and error handling
✅ Structured error responses
✅ Database connectivity (MongoDB)
✅ Storage service initialization (MinIO)

## What's Not Yet Implemented

The following features are planned for later phases:

⏳ Actual story generation (Phase 2 - LLM agents)
⏳ Image generation (Phase 3)
⏳ Celery job queue (Phase 2)
⏳ Real-time progress updates (Phase 4)
⏳ Frontend integration (Phase 4)

## Next Steps

Once Phase 1 testing is complete:
1. Merge `phase-1/core-backend-api` branch to `main`
2. Begin Phase 2: LLM Agent System implementation
3. Start frontend development in parallel
