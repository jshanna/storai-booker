# Phase 2 Complete: LLM Agent System with Google Gemini

## Overview

Phase 2 implementation is complete! The StorAI-Booker backend now includes a fully functional multi-agent story generation system powered by Google Gemini.

## What Was Implemented

### 1. LLM Provider Abstraction Layer
- **Base Provider Interface** (`app/services/llm/base.py`)
  - Abstract class defining common LLM operations
  - Support for text generation and structured output

- **Google Gemini Provider** (`app/services/llm/google_provider.py`)
  - Integration with Google's Gemini API via LangChain
  - Supports `gemini-1.5-pro-latest` (quality) and `gemini-1.5-flash-latest` (speed)
  - Structured output using Pydantic models
  - Automatic retry logic with exponential backoff

- **Provider Factory** (`app/services/llm/provider_factory.py`)
  - Factory pattern for creating provider instances
  - Configuration from environment variables

### 2. Prompt Templates
Located in `app/services/llm/prompts/`:

- **Story Planning** (`story_planning.py`)
  - Prompts for the Coordinator Agent
  - Age-appropriate guidelines for 5 age groups (3-4, 5-6, 7-8, 9-10, 11-12)
  - Structured output: character descriptions, story outline, page outlines

- **Page Generation** (`page_generation.py`)
  - Prompts for Page Generator Agents
  - Context-aware (includes previous page for continuity)
  - Generates both narrative text and illustration prompts

- **Validation** (`validation.py`)
  - Prompts for Validator Agent
  - Checks character consistency, narrative flow, age-appropriateness
  - Returns structured issues with severity levels

### 3. Agent Services
Located in `app/services/agents/`:

- **Coordinator Agent** (`coordinator.py`)
  - Phase 1 of story generation
  - Takes user inputs and creates complete story plan
  - Expands characters, creates story outline, generates page outlines

- **Page Generator Agent** (`page_generator.py`)
  - Phase 2 of story generation
  - Generates individual page content (text + illustration prompt)
  - Supports regeneration for failed validation

- **Validator Agent** (`validator.py`)
  - Phase 3 of story generation
  - Validates complete stories for quality and coherence
  - Identifies pages needing regeneration
  - Supports both full story and individual page validation

### 4. Celery Task System
- **Celery App** (`app/services/celery_app.py`)
  - Redis-based broker and result backend
  - Task routing by queue (story_generation, page_generation, validation)
  - Progress tracking enabled
  - Result expiry: 1 hour

- **Story Generation Tasks** (`app/tasks/story_generation.py`)
  - `generate_story_task`: Main orchestration task
  - `generate_page_task`: Individual page generation (for parallel execution)
  - `validate_story_task`: Story validation task
  - Automatic retry logic on failures
  - Progress updates throughout generation

### 5. API Integration
- **Stories API** (`app/api/stories.py`)
  - Connected to Celery task queue
  - `POST /api/stories/generate` now queues generation task
  - `GET /api/stories/{id}/status` tracks progress
  - Status transitions: pending → generating → complete/error

### 6. Docker Configuration
- **Updated `docker-compose.yml`**
  - Celery worker service with all environment variables
  - Flower monitoring on port 5555
  - LLM provider settings passed from .env
  - Health checks for all services

### 7. Comprehensive Tests
- **LLM Provider Tests** (`tests/test_llm_providers.py`)
  - Tests for Google Gemini provider
  - Factory pattern tests
  - Structured output parsing tests

- **Agent Tests** (`tests/test_agents.py`)
  - Tests for all three agents
  - Mocked LLM responses
  - Edge case handling

- **Story Generation Tests** (`tests/test_story_generation.py`)
  - End-to-end workflow tests
  - Validation and regeneration tests
  - Progress tracking tests

### 8. End-to-End Test Script
- **`backend/test_phase2_e2e.py`**
  - Executable test script
  - Tests complete story generation flow
  - Validates all agents and integrations
  - Provides clear output and error messages

## Files Created

### New Files (26 total)
```
backend/app/services/llm/
├── __init__.py
├── base.py
├── google_provider.py
├── provider_factory.py
└── prompts/
    ├── __init__.py
    ├── story_planning.py
    ├── page_generation.py
    └── validation.py

backend/app/services/agents/
├── __init__.py
├── coordinator.py
├── page_generator.py
└── validator.py

backend/app/services/
└── celery_app.py

backend/app/tasks/
├── __init__.py
└── story_generation.py

backend/tests/
├── test_llm_providers.py
├── test_agents.py
└── test_story_generation.py

backend/
├── test_phase2_e2e.py
└── PHASE2_COMPLETE.md (this file)
```

### Modified Files (3 total)
```
backend/app/api/stories.py (added Celery task call)
backend/.env (updated LLM provider defaults)
docker-compose.yml (added LLM env vars)
```

## Getting Started

### 1. Set Up Google Gemini API Key

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update `backend/.env`:
   ```bash
   GOOGLE_API_KEY=your-actual-api-key-here
   ```

### 2. Start Services

```bash
# Start all services including Celery workers
docker compose --profile full up -d

# Verify services are running
docker compose ps

# Check logs
docker compose logs -f celery-worker
docker compose logs -f backend
```

### 3. Run End-to-End Test

```bash
cd backend
python test_phase2_e2e.py
```

Expected output:
```
✓ LLM Provider: Connected
✓ Coordinator Agent: Generated metadata
✓ Page Generator Agent: Generated 3 pages
✓ Validator Agent: Validation passed
✓ ALL TESTS PASSED!
```

### 4. Test via API

```bash
# Create a story
curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Brave Squirrel",
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

# Get story ID from response, then check status
curl http://localhost:8000/api/stories/{STORY_ID}/status

# Get complete story
curl http://localhost:8000/api/stories/{STORY_ID}
```

### 5. Monitor with Flower

Open http://localhost:5555 to view:
- Active tasks
- Task history
- Worker status
- Task progress

## Story Generation Flow

### 1. User Submits Request
```
POST /api/stories/generate
```

### 2. API Creates Pending Story
- Storybook document created in MongoDB
- Status: "pending"
- Celery task queued

### 3. Coordinator Agent Plans Story
- Expands character descriptions
- Creates story outline
- Generates page outlines (one per page)
- Creates illustration style guide
- Updates `storybook.metadata`

### 4. Page Agents Generate Pages
- For each page:
  - Uses page outline + story context
  - Generates narrative text
  - Generates detailed illustration prompt
  - Appends to `storybook.pages`
- Progress updated after each page

### 5. Validator Agent Checks Quality
- Validates:
  - Character consistency
  - Narrative flow
  - Age-appropriateness
  - Story coherence
  - Illustration prompt quality
- If issues found:
  - Moderate/critical issues → regenerate pages
  - Minor issues → accept
- Re-validates after regeneration

### 6. Story Complete
- Status: "complete"
- All pages have `validated: true`
- `illustration_url` is None (Phase 3)

## Data Models

### GenerationInputs
```python
{
  "audience_age": 7,
  "topic": "A brave squirrel...",
  "setting": "Enchanted forest...",
  "format": "storybook",
  "illustration_style": "watercolor",
  "characters": ["Hazel the squirrel"],
  "page_count": 10
}
```

### StoryMetadata (generated by Coordinator)
```python
{
  "character_descriptions": [
    {
      "name": "Hazel",
      "physical_description": "A small brown squirrel...",
      "personality": "Brave, curious, kind-hearted",
      "role": "protagonist"
    }
  ],
  "character_relations": "Hazel is the main character...",
  "story_outline": "Beginning: ... Middle: ... End: ...",
  "page_outlines": [
    "Page 1: Hazel stands at forest edge...",
    "Page 2: Hazel meets talking owl...",
    ...
  ],
  "illustration_style_guide": "Watercolor with soft edges..."
}
```

### Page (generated by Page Agent)
```python
{
  "page_number": 1,
  "text": "Hazel the squirrel stood at the edge...",
  "illustration_prompt": "A small brown squirrel with bright eyes...",
  "illustration_url": null,  // Phase 3
  "generation_attempts": 1,
  "validated": true
}
```

## Cost Estimates

Using **Gemini 1.5 Flash** (recommended for development):
- Input: ~$0.075 per 1M tokens
- Output: ~$0.30 per 1M tokens

Per 10-page story:
- ~20-30k tokens total
- **Cost: ~$0.01-0.02 per story**

Free tier: 1,500 requests/day = ~100 stories/day

Using **Gemini 1.5 Pro** (recommended for production):
- Input: ~$1.25 per 1M tokens
- Output: ~$5.00 per 1M tokens
- **Cost: ~$0.15-0.25 per story**

## Configuration

### LLM Models

Edit `backend/.env`:

```bash
# For speed during development
DEFAULT_TEXT_MODEL=gemini-1.5-flash-latest

# For quality in production
DEFAULT_TEXT_MODEL=gemini-1.5-pro-latest

# Experimental (free during preview)
DEFAULT_TEXT_MODEL=gemini-2.0-flash-exp
```

### Retry Settings

Edit `backend/.env`:

```bash
DEFAULT_RETRY_LIMIT=3  # Max regeneration attempts per page
DEFAULT_MAX_CONCURRENT_PAGES=5  # Not used yet (sequential generation)
```

### Celery Settings

Edit `backend/app/services/celery_app.py`:

```python
task_time_limit=1800,  # 30 minutes max per task
task_soft_time_limit=1500,  # 25 minutes soft limit
result_expires=3600,  # 1 hour result storage
```

## Troubleshooting

### "API key not configured"
- Check `GOOGLE_API_KEY` in `backend/.env`
- Restart services: `docker compose --profile full restart`

### "Celery worker not processing tasks"
- Check worker is running: `docker compose ps celery-worker`
- View logs: `docker compose logs celery-worker`
- Check Redis: `docker compose ps redis`

### "Story stuck in 'generating' status"
- Check Flower dashboard: http://localhost:5555
- View task details and errors
- Check worker logs for exceptions

### "Validation keeps failing"
- Check prompt quality in `app/services/llm/prompts/`
- Reduce `DEFAULT_RETRY_LIMIT` to prevent infinite loops
- View validation issues in story response

### "Tests failing"
- Ensure MongoDB is running: `docker compose ps mongodb`
- Check test database connection in logs
- Run with verbose output: `pytest -v tests/`

## Next Steps

### Phase 3: Image Generation
- Integrate image generation API (DALL-E, Stable Diffusion, or Gemini Imagen)
- Populate `page.illustration_url` for each page
- Generate cover image
- Store images in MinIO/S3

### Phase 4: Frontend Development
- Build React/Next.js UI
- Story creation form
- Real-time progress tracking
- Story viewer with page navigation
- Image display and download

### Phase 5: Advanced Features
- Multiple illustration styles
- Character customization
- Story variations and branching
- Export to PDF/EPUB
- Comic book format support

## Success Criteria ✅

All Phase 2 success criteria have been met:

- ✅ Gemini provider working with structured outputs
- ✅ Coordinator agent generates complete StoryMetadata
- ✅ Page agents generate text + illustration prompts for all pages
- ✅ Validation agent checks coherence and age-appropriateness
- ✅ Celery workers process tasks in Docker
- ✅ Status transitions work (pending → generating → complete)
- ✅ Progress tracking functional via API endpoint
- ✅ Error handling and retry logic implemented
- ✅ Tests passing for all components
- ✅ Can generate a complete storybook end-to-end

## Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google Generative AI](https://python.langchain.com/docs/integrations/chat/google_generative_ai)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Beanie ODM Documentation](https://beanie-odm.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check this documentation
2. Review test output from `test_phase2_e2e.py`
3. Check Celery worker logs
4. Review Flower dashboard
5. Examine validation output in story responses

---

**Phase 2 Implementation Complete! 🎉**

The StorAI-Booker backend is now capable of generating complete storybooks with AI-powered narrative text and illustration prompts.
