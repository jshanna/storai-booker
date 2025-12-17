# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StorAI-Booker is an AI-powered storybook and comic book generation application that uses LLMs to create personalized, illustrated stories for children. The application features a Python FastAPI backend with MongoDB for data persistence, and a React TypeScript frontend.

**Current Status:** Phase 1 Complete (Core Backend API). The project is on branch `phase-1/core-backend-api` with a functional REST API for story management and settings.

## Essential Commands

### Starting the Application

```bash
# Start infrastructure (MongoDB, Redis, MinIO)
docker compose up -d

# Backend (from backend/ directory)
poetry install
poetry shell
python main.py

# Frontend (from frontend/ directory)
npm install
npm run dev
```

### Testing

```bash
# Backend tests (from backend/)
poetry run pytest                          # Run all tests
poetry run pytest --cov=app               # With coverage
poetry run pytest tests/test_api_stories.py  # Specific test file

# Backend code quality
poetry run ruff check .                    # Linting
poetry run black .                         # Formatting
poetry run mypy .                          # Type checking
```

### Docker Services

```bash
# Core services only (MongoDB, Redis, MinIO)
docker compose up -d

# All services including backend and Celery
docker compose --profile full up -d

# View logs
docker compose logs -f [service-name]

# Stop everything
docker compose down
docker compose down -v  # Also remove volumes
```

## Architecture

### Multi-Agent Story Generation System

The core feature is a coordinated multi-agent system for generating stories:

1. **Coordinating Agent**: Orchestrates the generation process
   - Expands character descriptions
   - Creates story outlines and page breakdowns
   - Manages panel layouts for comic books
   - Validates coherence and age-appropriateness

2. **Page Agents**: Work in parallel to generate individual pages
   - Traditional storybooks: Generate narrative text + illustration prompts
   - Comic books: Generate panel-by-panel content (dialogue, action, speech bubbles, sound effects)

3. **Assembly & Validation**: Ensures consistency across all pages
   - Character consistency checks
   - Narrative flow validation
   - Error detection and regeneration (with retry limits)

This system is not yet implemented (Phase 2) but shapes the data models and API design.

### Backend Architecture (Python + FastAPI)

**Tech Stack:**
- FastAPI for async REST API
- MongoDB with Beanie ODM (async Pydantic-based)
- Motor for async MongoDB driver
- Celery + Redis for job queuing (future)
- MinIO/S3 for image storage
- LangChain for LLM orchestration (future)

**Key Directories:**
- `backend/app/api/`: API route handlers
- `backend/app/models/`: Beanie ODM models (MongoDB documents)
- `backend/app/schemas/`: Pydantic schemas for request/response validation
- `backend/app/services/`: Business logic (storage, agents, LLM)
- `backend/app/core/`: Configuration and database initialization
- `backend/app/middleware/`: Error handlers and middleware

**Important Design Patterns:**
- Settings managed via Pydantic Settings with environment variables
- All database operations use async/await with Beanie ODM
- MongoDB stores complete story documents with embedded pages/panels
- Storage service uses boto3 for S3-compatible object storage (MinIO locally)
- Error handling uses FastAPI exception handlers with structured responses

### Data Models

**Storybook Document** (`backend/app/models/storybook.py`):
- Stores complete stories as single MongoDB documents
- Embeds generation inputs, metadata, and pages as subdocuments
- Supports both traditional storybook and comic book formats
- Comic books have panels with dialogue, speech bubbles, and sound effects

**Settings Document** (`backend/app/models/settings.py`):
- Singleton document storing application configuration
- LLM provider settings (API keys, model selections)
- Story generation defaults and content filters
- Uses `get_settings()` helper for singleton pattern

**Key Fields:**
- `format`: "storybook" or "comic" determines generation path
- `status`: "pending" | "generating" | "complete" | "error"
- Comic-specific: `panels`, `panelsPerPage`, `dialogue`, `soundEffects`

### Frontend Architecture (React + TypeScript)

**Tech Stack:**
- React 18 with TypeScript
- Vite for build tooling
- React Router v6 for routing
- Zustand for state management
- React Query for API interactions
- React Hook Form + Zod for form validation

**Structure:**
- `frontend/src/components/`: Reusable UI components
- `frontend/src/pages/`: Page-level components (Generation, Library, Settings, Reader)
- `frontend/src/services/`: API client services
- `frontend/src/store/`: Zustand state stores
- `frontend/src/types/`: TypeScript type definitions

**API Integration:**
- Vite proxy configured to forward `/api/*` to `http://localhost:8000`
- All API calls should use relative paths like `/api/stories`

### LLM Provider Support

The application supports multiple LLM providers (implementation in Phase 2):
- **OpenAI**: GPT-4 for text, DALL-E 3 for images
- **Anthropic**: Claude for text generation
- **Google**: Gemini for text, Gemini 2.5 Flash Image for image generation (see `docs/GEMINI_MODELS.md`)
  - Image Generation: https://ai.google.dev/gemini-api/docs/image-generation
  - Consistent Character Imagery: https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/media-generation/consistent_imagery_generation.ipynb

Provider configuration stored in Settings model with API keys encrypted at rest.

## Development Workflow

### Git Repository Management

**IMPORTANT: Always commit and push changes after completing and testing work**

After completing any feature, fix, or significant change:
1. Test the changes thoroughly (run tests, verify functionality)
2. Stage all changes: `git add -A`
3. Commit with a descriptive message (include phase info if applicable)
4. Push to remote: `git push`
5. Verify repository is clean: `git status`

This ensures:
- Work is backed up and versioned
- Changes are available for other sessions
- History is well-documented
- Repository stays synchronized

### Phase-Based Development

The project follows a 6-phase development plan (see `specs/development-plan.md`):
- **Phase 0**: Setup (Complete)
- **Phase 1**: Core Backend API (Complete)
- **Phase 2**: LLM Agent System (Complete)
- **Phase 3**: Image Generation (Complete)
- **Phase 4**: Frontend Development (Complete)
- **Phase 5**: Production Ready (In Progress - Security Hardening Complete)
- **Phase 6**: Advanced Features

### Current Project Status

**Completed:**
- ✅ Phase 0: Project Setup
- ✅ Phase 1: Core Backend API (CRUD, pagination, filtering)
- ✅ Phase 2: LLM Agent System (multi-agent story generation with Google Gemini)
- ✅ Phase 3: Image Generation (Gemini 2.5 Flash Image with character consistency)
- ✅ Phase 4: Frontend Development (React UI with generation, library, reader, settings)
- ✅ Phase 5.1: Testing (50% coverage, integration tests)
- ✅ Phase 5.2: Performance Optimization (caching, lazy loading, indexes)
- ✅ Phase 5.3: Security Hardening (rate limiting, input sanitization, security headers)
- 🚧 Phase 5.4: Error Handling & Logging (next)
- 🚧 Phase 5.5: Documentation
- 🚧 Phase 5.6: CI/CD Pipeline

**Key Features Working:**
- Full story generation pipeline (text + images)
- Character consistency across pages using reference images
- Age-appropriate content filtering
- Story validation and regeneration
- Production deployment with Docker Compose
- MinIO storage with nginx proxy for images
- Comprehensive security measures

### Working with MongoDB

This project uses MongoDB (not PostgreSQL/relational) because:
- Stories have flexible schemas (traditional vs comic format)
- Natural representation of nested pages/panels/dialogue
- No complex migrations needed for schema changes
- GridFS available for large file storage if needed

**Key Patterns:**
```python
# Always use Beanie ODM for database operations
from app.models.storybook import Storybook

# Find documents
story = await Storybook.get(story_id)  # By ID
stories = await Storybook.find_all().to_list()  # All

# Create documents
story = Storybook(**data)
await story.insert()

# Update documents
await story.set({Storybook.status: "complete"})

# Delete documents
await story.delete()
```

### Environment Variables

Backend configuration is loaded from `backend/.env`:
- Copy `backend/.env.example` to `backend/.env` for defaults
- MongoDB, Redis, MinIO URLs configured for docker-compose defaults
- LLM API keys should be added when implementing Phase 2
- All settings use Pydantic Settings with type validation

### API Conventions

**Endpoints:**
- All API routes prefixed with `/api`
- Stories: `/api/stories/*`
- Settings: `/api/settings/*`
- OpenAPI docs: `/api/docs` (Swagger), `/api/redoc` (ReDoc)

**Response Format:**
- Success: Return Pydantic model as JSON
- Error: Structured error responses with `detail` field
- Pagination: `page`, `page_size`, `total`, `pages` fields
- List responses: Include count and items array

**Validation:**
- All request bodies use Pydantic schemas (in `backend/app/schemas/`)
- Age validation: 3-12 years (configurable in settings)
- Page count: 1-50 pages
- Panels per page: 1-9 (comic format only)

## Important Constraints

### Story Generation (Phase 2+)

When implementing the LLM agent system:
- Use LangChain for agent orchestration
- Implement runaway prevention (hard limits on LLM calls)
- Retry limit default: 3 attempts per page
- Maximum concurrent page generations: 5 (configurable)
- Age-appropriate content validation is mandatory
- NSFW filter enabled by default

### Comic Book Rendering (Phase 3+)

For comic book panel composition:
- Use Pillow (PIL) for image manipulation in Python backend
- Panel layouts: grid-based (2x2, 3x1, etc.) or custom
- Speech bubbles: SVG generation with cairosvg for rasterization
- Text overlay: PIL ImageDraw with custom fonts
- Final composition: Combine panels with borders/gutters into single page image

### Content Safety

All generated content must pass:
- Age-appropriate vocabulary and themes
- NSFW filter (using LLM moderation APIs)
- Violence/scary content filters (configurable)
- Character consistency validation

## Testing Guidelines

### Backend Testing

Use pytest with async support:
```python
# Test fixture pattern (see backend/tests/conftest.py)
@pytest.fixture
async def test_db():
    await init_test_database()
    yield
    await cleanup_test_database()

# Test API endpoints
async def test_create_story(client: AsyncClient):
    response = await client.post("/api/stories/generate", json=payload)
    assert response.status_code == 200
```

**Coverage Target:** >80% for core business logic

### Integration Testing

See `PHASE1_TESTING.md` for comprehensive testing guide including:
- Docker service verification
- API endpoint testing with curl
- Error handling validation
- Pagination and filtering tests

## Common Patterns

### Adding a New API Endpoint

1. Define Pydantic schema in `backend/app/schemas/`
2. Create route handler in `backend/app/api/`
3. Include router in `backend/main.py`
4. Write tests in `backend/tests/`
5. Update OpenAPI docs automatically (FastAPI generates them)

### Adding a New Service

1. Create service class in `backend/app/services/`
2. Use singleton pattern if stateless (like `storage_service`)
3. Inject dependencies via FastAPI dependency injection if needed
4. Add health check method if service has external dependencies

### Working with Settings

```python
# Get application settings
from app.core.config import settings
print(settings.mongodb_url)

# Get user-configured settings from database
from app.models.settings import get_settings
app_settings = await get_settings()
```

## Reference Documentation

- **Application Spec**: `specs/application-spec.md` - Complete feature specification
- **Development Plan**: `specs/development-plan.md` - 6-phase implementation roadmap
- **Testing Guide**: `TESTING.md` - Local testing instructions
- **Phase 1 Testing**: `PHASE1_TESTING.md` - Detailed API testing guide
- **Quick Start**: `QUICK_START.md` - 5-minute setup guide
- **Gemini Models**: `docs/GEMINI_MODELS.md` - Google Gemini provider documentation
- **Gemini Image Generation**: https://ai.google.dev/gemini-api/docs/image-generation - Official Gemini image generation API docs
- **Consistent Character Imagery**: https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/media-generation/consistent_imagery_generation.ipynb - Guide for character consistency with reference images

## Known Limitations

- Story generation currently returns mock data (Phase 1 API skeleton)
- Image generation not implemented yet (Phase 3)
- No user authentication system (Phase 6)
- No real-time WebSocket updates yet (Phase 4)
- Comic book panel composition not implemented (Phase 3)
- Celery workers not active (Phase 2)

## Development Tips

- Use `poetry shell` to activate the Python virtual environment for backend work
- MongoDB documents are validated by Beanie at runtime; schema changes don't require migrations
- Frontend proxies API requests via Vite config; backend must run on port 8000
- Docker services must be running for backend to function (MongoDB, Redis, MinIO)
- MinIO console (http://localhost:9001) useful for debugging image storage
- FastAPI auto-generates OpenAPI docs; use `/api/docs` for interactive testing
