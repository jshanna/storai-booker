# StorAI-Booker Backend

AI-powered children's storybook and comic book generation backend built with FastAPI, Celery, and Google Gemini.

## Features

### Phase 1: Core Backend API ✅
- FastAPI REST API with async support
- MongoDB document storage (Beanie ODM)
- MinIO/S3 object storage for images
- Redis caching and Celery task queue
- Comprehensive error handling and validation

### Phase 2: LLM Agent System ✅
- **Coordinator Agent**: Story planning and metadata generation
- **Page Generator Agent**: Individual page text and illustration prompts
- **Validator Agent**: Quality assurance and consistency checking
- Google Gemini integration (gemini-2.5-flash)
- Automatic retry and regeneration logic

### Phase 3: Image Generation ✅
- **Google Gemini Image Generation**: AI-generated page illustrations
- **Cover Creation**: Custom covers with title overlays
- **Image Compositor**: PIL/Pillow-based text overlays and effects
- **Storage Integration**: Automatic upload to MinIO/S3 with signed URLs
- **Graceful Degradation**: Stories complete even if image generation fails

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (Python dependency manager)
- Docker & Docker Compose (for MongoDB, Redis, MinIO)
- Google API Key (for Gemini text and image generation)

### Installation

1. **Install dependencies:**
```bash
cd backend
poetry install
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

3. **Start infrastructure services:**
```bash
docker compose --profile full up -d
```

This starts:
- MongoDB (port 27017)
- Redis (port 6379)
- MinIO (port 9000, console: 9001)
- Celery Worker
- Flower (Celery monitoring: port 5555)

4. **Run the API server:**
```bash
poetry run python main.py
# or
poetry shell
python main.py
```

The API will be available at http://localhost:8000

## Testing

### Run All Tests
```bash
poetry run pytest
```

Current test coverage includes:
- API endpoint integration tests
- Database operation tests
- Error handling tests

Note: For comprehensive testing, use the main test suite. E2E testing is done via manual testing through the frontend.

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Flower (Celery)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001

## Configuration

Key environment variables in `.env`:

```bash
# Google Gemini API
GOOGLE_API_KEY=your-api-key-here
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.0-flash-exp

# Image Generation
IMAGE_ASPECT_RATIO=16:9
IMAGE_MAX_RETRIES=3
COVER_ASPECT_RATIO=3:4

# Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=storai-booker-images

# Database
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Configuration and settings
│   ├── models/           # Beanie/Pydantic models
│   ├── services/
│   │   ├── agents/       # LLM agents (coordinator, page generator, validator)
│   │   ├── image/        # Image generation & composition
│   │   ├── llm/          # LLM providers & prompts
│   │   ├── celery_app.py
│   │   └── storage.py    # MinIO/S3 client
│   ├── tasks/            # Celery background tasks
│   └── middleware/       # Error handlers
├── tests/                # Pytest test suite
├── main.py               # FastAPI entry point
├── pyproject.toml        # Python dependencies
└── README.md
```

## Development Workflow

### Creating a Story

1. **POST** `/api/stories/generate` with story parameters:
```json
{
  "audience_age": 7,
  "topic": "A brave squirrel exploring a magical forest",
  "setting": "Enchanted forest with talking animals",
  "format": "storybook",
  "illustration_style": "watercolor",
  "characters": ["Hazel the squirrel"],
  "page_count": 10
}
```

2. **Monitor progress** via Celery task ID or poll `/api/stories/{id}/status`

3. **Retrieve completed story** at `/api/stories/{id}`

The story will include:
- Generated narrative text for each page
- Illustration prompts and generated images
- Custom cover image with title overlay
- All images uploaded to MinIO with signed URLs

## Cost Estimates

Using Google Gemini Free Tier/Pay-as-you-go:

- **Text Generation** (Phase 2): ~$0.20-0.40 per story
- **Image Generation** (Phase 3): ~$0.43 per story (11 images @ $0.039 each)
- **Total**: ~$0.60-0.85 per 10-page illustrated storybook

For 100 stories/month: **~$60-85/month**

## Architecture

```
Client Request
    ↓
FastAPI API (main.py)
    ↓
Celery Task Queue (story_generation.py)
    ↓
┌─────────────────────────────────────┐
│ Story Generation Workflow           │
│                                     │
│ 1. Coordinator Agent                │
│    └─ Plan story & characters       │
│                                     │
│ 2. Page Generator Agent (loop)      │
│    ├─ Generate page text            │
│    ├─ Generate illustration prompt  │
│    └─ Generate & upload image       │
│                                     │
│ 3. Validator Agent                  │
│    └─ Check quality & consistency   │
│                                     │
│ 4. Cover Generator                  │
│    ├─ Generate cover image          │
│    ├─ Add title overlay             │
│    └─ Upload to storage             │
└─────────────────────────────────────┘
    ↓
MongoDB (metadata & text)
MinIO/S3 (images)
```

## Next Steps

- **Phase 5**: Production readiness (performance, testing, security)
- **Phase 6**: Advanced features (user accounts, PDF export, sharing)

## License

Proprietary - Portfolio Project
