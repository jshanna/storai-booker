# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StorAI-Booker is an AI-powered storybook and comic book generation application that uses LLMs to create personalized, illustrated stories for children. The application features a Python FastAPI backend with MongoDB for data persistence, and a React TypeScript frontend.

**Current Status:** Phase 6 (Advanced Features). The project has a fully functional story and comic generation pipeline with AI-powered image generation, critic review system, user authentication, and export capabilities.

## ⚠️ CRITICAL SECURITY WARNING

**NEVER COMMIT API KEYS OR SECRETS TO GIT**

- `.env`, `.env.production`, `.env.staging` and similar files contain sensitive credentials
- These files are in `.gitignore` and should NEVER be committed to the repository
- Always use placeholder values in example files (`.env.example`, `.env.production.example`)
- If you accidentally expose an API key (even in chat), it MUST be rotated immediately
- Real API keys should only exist in:
  - Local `.env` files (gitignored)
  - Production environment variables (server/container config)
  - Secure secrets management systems (AWS Secrets Manager, etc.)

**Before Reading/Modifying Environment Files:**
- Verify the file is gitignored before reading it
- Never output API keys in responses
- Use placeholders like `your_api_key_here` when showing examples

**API Key Security Checklist:**
- ✅ All `.env*` files are in `.gitignore`
- ✅ Only `.env.example` files are committed (with placeholders)
- ✅ Real API keys are never in git history
- ✅ Exposed keys are rotated immediately

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

1. **Coordinating Agent** (`backend/app/services/agents/coordinator.py`): Orchestrates the generation process
   - Creates story outlines and page breakdowns
   - Generates character descriptions from user input
   - Defines illustration style guides
   - Validates coherence and age-appropriateness

2. **Page Generator Agent** (`backend/app/services/agents/page_generator.py`): Generates individual pages
   - Traditional storybooks: Generate narrative text + illustration prompts
   - Comic books: Generate panel scripts (dialogue, captions, sound effects, layout)

3. **Validator Agent** (`backend/app/services/agents/validator.py`): Ensures quality
   - Validates story coherence
   - Checks age-appropriateness
   - Triggers regeneration if issues found

4. **Critic System** (`backend/app/services/agents/critics/`): Reviews generated comic pages
   - **CompositionCritic** (35% weight): Reviews panel layout, visual balance, reading flow
   - **StoryCritic** (35% weight): Reviews narrative coherence, character consistency
   - **TechnicalCritic** (30% weight): Reviews image quality, age-appropriateness
   - Uses vision-based multimodal LLM analysis
   - Pages below 6.5/10 threshold are regenerated (max 3 revisions)

### Comic Book Generation Flow

Comics use **whole-page generation** (not per-panel):
1. Page Generator creates panel scripts with dialogue/captions/effects
2. Whole-page image prompt is built from all panel content
3. Gemini 2.5 Flash generates complete comic page as single image
4. Three critics review the generated image in parallel
5. If score < 6.5, regenerate with critic feedback
6. Final image stored with dialogue/effects baked in

### Backend Architecture (Python + FastAPI)

**Tech Stack:**
- FastAPI for async REST API
- MongoDB with Beanie ODM (async Pydantic-based)
- Motor for async MongoDB driver
- Celery + Redis for background job processing
- MinIO/S3 for image storage
- Google Gemini for text generation and image generation

**Key Directories:**
- `backend/app/api/`: API route handlers
- `backend/app/models/`: Beanie ODM models (MongoDB documents)
- `backend/app/schemas/`: Pydantic schemas for request/response validation
- `backend/app/services/`: Business logic (storage, agents, LLM, export)
- `backend/app/services/agents/`: Multi-agent story generation system
- `backend/app/services/agents/critics/`: Vision-based critic agents for quality review
- `backend/app/services/llm/`: LLM provider implementations and prompts
- `backend/app/services/export/`: PDF, EPUB, CBZ export services
- `backend/app/tasks/`: Celery background tasks (story generation)
- `backend/app/core/`: Configuration and database initialization
- `backend/app/middleware/`: Error handlers and middleware

**Important Design Patterns:**
- Settings managed via Pydantic Settings with environment variables
- All database operations use async/await with Beanie ODM
- MongoDB stores complete story documents with embedded pages/panels
- Storage service uses boto3 for S3-compatible object storage (MinIO locally)
- Error handling uses FastAPI exception handlers with structured responses

**Pydantic v2 Compatibility:**
- Use `model_config = ConfigDict(...)` instead of `class Config:` (deprecated)
- For Beanie ODM queries, use dict syntax: `User.find_one({"email": email})` not `User.find_one(User.email == email)`
- Indexed fields: `field: Indexed(str) = Field(..., description="...")  # type: ignore`

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

Currently using **Google Gemini** for all AI operations:
- **Text Generation**: Gemini 2.0 Flash for story planning, page generation, validation
- **Image Generation**: Gemini 2.5 Flash Image for illustrations and comic pages
- **Vision Analysis**: Gemini 2.0 Flash for critic review of generated images

Key features:
- Character consistency using reference images passed to image generation
- Whole-page comic generation with dialogue/effects baked into images
- Vision-based multimodal critics for quality review
- Age-appropriate content prompts throughout the pipeline

See `docs/GEMINI_MODELS.md` for detailed model documentation.

Provider configuration stored in Settings model. API keys should be set via environment variables.

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
- **Phase 5**: Production Ready (Complete)
- **Phase 6**: Advanced Features (In Progress - Auth, Export, Comics, Templates complete)

### Current Project Status

**Completed:**
- ✅ Phase 0: Project Setup
- ✅ Phase 1: Core Backend API (CRUD, pagination, filtering)
- ✅ Phase 2: LLM Agent System (multi-agent story generation with Google Gemini)
- ✅ Phase 3: Image Generation (Gemini 2.5 Flash Image with character consistency)
- ✅ Phase 4: Frontend Development (React UI with generation, library, reader, settings)
- ✅ Phase 5: Production Ready (testing, optimization, security, auth)
- ✅ Phase 6.1: User Authentication (JWT, OAuth with GitHub/Google)
- ✅ Phase 6.2: Export System (PDF, EPUB, CBZ formats)
- ✅ Phase 6.3: Comic Book Format (whole-page generation with critic review)
- ✅ Phase 6.4: Story Templates
- 🚧 Phase 6.5: Advanced Features (in progress)

**Key Features Working:**
- Full storybook generation pipeline (text + per-page illustrations)
- Comic book generation with whole-page images (dialogue/effects baked in)
- Three-critic review system for comic page quality
- Character consistency using reference images
- Age-appropriate content filtering throughout pipeline
- User authentication (local accounts + OAuth)
- Export to PDF, EPUB, and CBZ formats
- Story templates for quick generation
- Production deployment with Docker Compose
- MinIO storage with nginx proxy for images

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

### Story Generation

Generation uses Celery background tasks (`backend/app/tasks/story_generation.py`):
- Celery task timeout: 60 minutes soft limit, 75 minutes hard limit
- Retry limit: 3 attempts per page (configurable via `critic_max_revisions`)
- Pages are generated sequentially (character reference images need prior pages)
- Progress updates sent via Celery task state updates

### Comic Book Generation

Comics use whole-page generation (not per-panel composition):
- Gemini 2.5 Flash generates complete comic pages as single images
- Dialogue bubbles, captions, and sound effects are baked into the image
- Panel layouts are described in the prompt (e.g., "2x2 grid", "3x1 strip")
- Three critics review each page using vision analysis
- Quality threshold: 6.5/10 weighted score (configurable via `critic_quality_threshold`)
- Max revisions: 3 (configurable via `critic_max_revisions`)

Config settings in `backend/app/core/config.py`:
```python
whole_page_generation: bool = True  # Use whole-page vs per-panel
critic_quality_threshold: float = 6.5
critic_max_revisions: int = 3
critic_composition_weight: float = 0.35
critic_story_weight: float = 0.35
critic_technical_weight: float = 0.30
```

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

- No real-time WebSocket updates (progress shown via polling)
- Comic generation can take 10-20+ minutes for longer stories
- Character consistency relies on reference images (first page generates character sheets)
- Export PDFs may have varying quality depending on source image resolution
- No collaborative editing or sharing features yet

## Development Tips

- Use `poetry shell` to activate the Python virtual environment for backend work
- MongoDB documents are validated by Beanie at runtime; schema changes don't require migrations
- Frontend proxies API requests via Vite config; backend must run on port 8000
- Docker services must be running for backend to function (MongoDB, Redis, MinIO)
- MinIO console (http://localhost:9001) useful for debugging image storage
- FastAPI auto-generates OpenAPI docs; use `/api/docs` for interactive testing
