# 🧪 StorAI-Booker Testing Guide

Guide for testing the StorAI-Booker application.

## Testing Strategy

### Current Test Coverage (Phase 5.1 Complete)

**Backend:**
- ✅ API endpoint integration tests (pytest) - 14 tests
- ✅ Storage service unit tests - 10 tests
- ✅ Agent unit tests - 10 tests
- ✅ Prompt template tests - 10 tests
- ✅ Database operations tests
- ✅ Error handling tests
- ✅ **Overall: 44 passing tests, 49% coverage**
- ⏳ E2E workflow tests (deferred to Phase 5.3)

**Frontend:**
- ✅ Manual testing through UI
- ⏳ Component tests (Phase 5.3)
- ⏳ E2E tests with Playwright (Phase 5.3)

## Quick Test Checklist

### 1. Infrastructure Services ✅

```bash
# Start services
docker compose up -d

# Verify all running
docker compose ps

# Expected services:
# - storai-mongodb (port 27017)
# - storai-redis (port 6379)
# - storai-minio (ports 9000, 9001)
```

### 2. Backend API ✅

```bash
cd backend

# Run test suite
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=app

# Check API health
curl http://localhost:8000/health
```

**Expected pytest output:**
- All tests passing
- Coverage reports for app/ modules

### 3. Frontend Application ✅

```bash
cd frontend

# Build check
npm run build

# Development server
npm run dev

# Navigate to http://localhost:5173
```

## Manual Testing Guide

### Complete User Flow Test

#### Prerequisites
1. All services running (Docker + Backend + Celery + Frontend)
2. Google API key configured in backend/.env

#### Test Steps

**1. Settings Configuration**
```
→ Navigate to http://localhost:5173/settings
→ Add Google API key in "API Keys & Providers" tab
→ Click "Save Settings"
→ Verify success toast appears
```

**2. Story Generation**
```
→ Navigate to /generate
→ Fill in form:
   - Audience: Child's name and age (e.g., "Emma", 7)
   - Topic: "A brave squirrel exploring a magical forest"
   - Setting: "Enchanted forest"
   - Characters: "Hazel the squirrel"
   - Pages: 5-10
→ Click "Generate Story"
→ Monitor progress bar (should show phases)
→ Wait for completion (3-5 minutes)
```

**3. Library View**
```
→ Navigate to /library
→ Verify new story appears
→ Test search box (search by topic/title)
→ Test filter dropdown (All Stories/Storybook/Comic)
→ Test sort dropdown (Newest/Oldest/Title)
→ Click story card to open reader
```

**4. Story Reader**
```
→ Verify cover image loads
→ Verify title displays
→ Use Next/Previous buttons to navigate
→ Test keyboard navigation (Arrow keys)
→ Test fullscreen mode (button in bottom navigation)
→ Verify page numbers update
→ Exit reader
```

**5. Generation Artifacts**
```
→ In library, click three-dot menu on story card
→ Click "View Artifacts"
→ Check "Character Sheets" tab:
   - Verify reference images load
   - Verify character descriptions show
→ Check "Page Prompts" tab:
   - Verify story text shows
   - Verify illustration prompts show
→ Close dialog
```

**6. Story Deletion**
```
→ Click three-dot menu on story card
→ Click "Delete"
→ Confirm deletion
→ Verify story removed from library
```

## Backend Unit Tests

### Running Tests

```bash
cd backend
poetry shell

# All tests
pytest

# Specific test file
pytest tests/test_api_stories.py

# Specific test
pytest tests/test_api_stories.py::test_create_story

# With verbose output
pytest -v

# With coverage
pytest --cov=app

# Coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Quick summary
pytest -q
```

### Test Organization

```
backend/tests/
├── conftest.py              # Pytest fixtures & test database setup
├── test_api_stories.py      # Story CRUD endpoints (14 tests)
├── test_api_settings.py     # Settings endpoints (4 tests)
├── test_agents.py           # Agent unit tests (10 tests)
├── test_storage.py          # Storage service tests (10 tests)
├── test_prompts.py          # Prompt template tests (10 tests)
├── test_llm_providers.py    # LLM provider tests (12 tests, skipped)
└── test_story_generation.py # Workflow tests (7 tests, skipped)
```

### Coverage Summary (Phase 5.1)

**Excellent Coverage (80%+):**
- ✅ Models: 100%
- ✅ Schemas: 100%
- ✅ Story Planning Prompts: 100%
- ✅ Page Generation Prompts: 100%
- ✅ Validation Prompts: 97%
- ✅ Config: 96%
- ✅ Celery App: 92%
- ✅ Middleware: 88%
- ✅ Coordinator Agent: 88%
- ✅ Validator Agent: 87%
- ✅ Page Generator Agent: 82%
- ✅ Settings API: 81%
- ✅ Storage Service: 80%

**Integration Testing (Deferred to E2E):**
- ⏳ Story Generation Task: 9% (complex Celery workflows)
- ⏳ Google LLM Provider: 16% (SDK integration)
- ⏳ Image Services: 15-47% (Google Imagen integration)
- ⏳ Provider Factories: 30-35% (settings dependencies)
- ⏳ Stories API: 67% (async workflow endpoints)

## API Testing

### Using Swagger UI

1. Start backend: `poetry run python main.py`
2. Open http://localhost:8000/api/docs
3. Test endpoints interactively

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List stories
curl http://localhost:8000/api/stories

# Generate story
curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "audience_age": 7,
    "topic": "A brave squirrel",
    "setting": "Magical forest",
    "format": "storybook",
    "illustration_style": "watercolor",
    "characters": ["Hazel"],
    "page_count": 5
  }'

# Get story by ID
curl http://localhost:8000/api/stories/{story_id}

# Delete story
curl -X DELETE http://localhost:8000/api/stories/{story_id}
```

## Performance Testing

### Story Generation Time

Expected times for different page counts:
- 5 pages: ~2-3 minutes
- 10 pages: ~4-5 minutes
- 15 pages: ~6-8 minutes
- 20 pages: ~8-10 minutes

### Database Query Performance

```bash
# Monitor MongoDB queries
docker exec -it storai-mongodb mongosh

# Enable profiling
use storai
db.setProfilingLevel(2)

# Check slow queries
db.system.profile.find().sort({ts:-1}).limit(5)
```

## Debugging

### Backend Logs

```bash
# API server logs (in terminal running main.py)
# Shows request/response and errors

# Celery worker logs (in terminal running celery)
# Shows task execution and errors
```

### Frontend Logs

```bash
# Browser console (F12)
# Shows API calls, React errors, state changes

# Network tab
# Monitor API requests and responses
```

### Common Issues

**Story stuck at "Generating..."**
- Check Celery worker is running
- Check worker logs for errors
- Verify Google API key is valid
- Check for safety filter blocks in logs

**Images not loading**
- Verify MinIO is running
- Check S3_ENDPOINT_URL in .env
- Verify signed URLs haven't expired

**API errors**
- Check backend logs for stack traces
- Verify MongoDB is connected
- Check /health endpoint

## Test Data Cleanup

### Clear all stories

```bash
# Via MongoDB
docker exec -it storai-mongodb mongosh
use storai
db.storybooks.deleteMany({})
exit

# Via API
curl -X DELETE http://localhost:8000/api/stories/{story_id}
```

### Clear MinIO storage

```bash
# Access MinIO console
open http://localhost:9001

# Login: minioadmin / minioadmin
# Navigate to buckets → storai-booker-images
# Delete objects as needed
```

### Reset database

```bash
docker compose down -v
docker compose up -d
```

## CI/CD Testing (Future - Phase 5)

Planned automated testing:
- GitHub Actions for pytest on PR
- Frontend build checks
- Linting and type checking
- E2E tests with Playwright
- Coverage reports

---

**Current Status:** Phase 4 Complete - Manual testing functional
**Next Phase:** Phase 5 - Automated test suite expansion
**Last Updated:** 2025-12-16
