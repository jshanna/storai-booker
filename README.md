# 📚 StorAI-Booker

AI-powered storybook generation application using Google Gemini for creating personalized, illustrated children's stories.

![Project Status](https://img.shields.io/badge/Status-Phase%204%20Complete-success)
![License](https://img.shields.io/badge/License-Proprietary-blue)

## 🎯 Project Status: Phase 4 Complete ✅

**Current Phase:** Phase 4 - Frontend Development Complete
**Next Phase:** Phase 5 - Production Readiness

### What's Working Now

✅ **Full-Stack Application Ready**
- Complete React/TypeScript frontend with modern UI
- Full backend API with Google Gemini integration
- End-to-end story generation pipeline
- Character reference sheet generation for consistency
- Real-time generation progress tracking
- Mobile-responsive reader interface

✅ **Story Generation Features**
- AI-powered story planning and writing
- Character description expansion and consistency
- Age-appropriate content validation
- Automatic illustration generation
- Custom cover images with titles
- Graceful error handling and retry logic

✅ **User Interface**
- Multi-step generation form with validation
- Library with search, filter, and sort
- Full-screen story reader with page navigation
- Settings management for LLM providers
- Generation artifacts viewer (character sheets + prompts)
- Dark mode support

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (for infrastructure services)
- **Python 3.10+** with Poetry
- **Node.js 18+** with npm
- **Google API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 5-Minute Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd storai-booker

# 2. Start infrastructure (MongoDB, Redis, MinIO)
docker compose up -d

# 3. Setup backend
cd backend
poetry install
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
poetry run python main.py &

# 4. Start Celery worker (in another terminal)
cd backend
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info &

# 5. Setup frontend
cd frontend
npm install
npm run dev

# 6. Open browser
open http://localhost:5173
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- shadcn/ui component library
- React Query (server state)
- Zustand (client state)
- React Hook Form + Zod validation
- Tailwind CSS

**Backend:**
- Python 3.10+ with FastAPI
- MongoDB (Beanie ODM + Motor)
- Redis (caching & Celery broker)
- Celery (async task queue)
- Google Gemini (text & image generation)
- Pillow (image processing)
- MinIO (S3-compatible storage)

**Infrastructure:**
- Docker + Docker Compose
- MongoDB 7.0
- Redis 7
- MinIO (local S3)

### Multi-Agent Story Generation

```
User Input → FastAPI → Celery Queue
                           ↓
        ┌──────────────────────────────────┐
        │  Story Generation Pipeline       │
        │                                  │
        │  1. Coordinator Agent            │
        │     • Expand character details   │
        │     • Create story outline       │
        │     • Plan page breakdowns       │
        │                                  │
        │  2. Character Sheet Generation   │
        │     • Generate reference images  │
        │     • Upload to storage          │
        │                                  │
        │  3. Page Generator (sequential)  │
        │     • Generate page text         │
        │     • Create illustration prompt │
        │     • Generate & upload image    │
        │                                  │
        │  4. Validator Agent              │
        │     • Check consistency          │
        │     • Validate age-appropriateness│
        │     • Regenerate if needed       │
        │                                  │
        │  5. Cover Generator              │
        │     • Generate cover illustration│
        │     • Upload final image         │
        └──────────────────────────────────┘
                    ↓
        MongoDB (text & metadata)
        MinIO (images & cover)
```

## 📁 Project Structure

```
storai-booker/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Configuration & database
│   │   ├── models/         # Beanie ODM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── agents/     # LLM agents (coordinator, page, validator)
│   │   │   ├── image/      # Image generation & composition
│   │   │   ├── llm/        # LLM provider integration
│   │   │   ├── celery_app.py
│   │   │   └── storage.py  # MinIO/S3 storage service
│   │   ├── tasks/          # Celery background tasks
│   │   └── middleware/     # Error handlers
│   ├── tests/              # Pytest test suite
│   ├── main.py             # FastAPI entry point
│   └── pyproject.toml      # Python dependencies
│
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── generation/ # Multi-step form
│   │   │   ├── story/      # Library & story cards
│   │   │   ├── reader/     # Book reader & navigation
│   │   │   ├── settings/   # Settings management
│   │   │   ├── shared/     # Reusable components
│   │   │   └── ui/         # shadcn/ui components
│   │   ├── pages/          # Page components
│   │   ├── lib/
│   │   │   ├── api/        # API client
│   │   │   ├── hooks/      # React hooks
│   │   │   └── stores/     # Zustand stores
│   │   └── types/          # TypeScript types
│   └── package.json
│
├── specs/                   # Project specifications
├── docs/                    # Additional documentation
├── docker-compose.yml       # Infrastructure services
├── CLAUDE.md               # Guide for Claude Code
└── README.md               # This file
```

## 🎨 Features

### Story Generation
- **Personalized Stories**: Age-appropriate content (3-12 years)
- **Character Consistency**: Reference sheets for visual consistency
- **Multiple Styles**: Watercolor, digital art, cartoon, and more
- **Flexible Length**: 5-20 pages per story
- **Smart Validation**: Automatic quality and coherence checking
- **Error Recovery**: Retry logic with safety filter handling

### User Interface
- **Guided Form**: Step-by-step story creation
- **Real-time Progress**: Live updates during generation
- **Library Management**: Search, filter, sort your stories
- **Reader Mode**: Full-screen reading experience with page navigation
- **Mobile Responsive**: Works on phones and tablets
- **Generation Artifacts**: View character sheets and prompts

### Settings & Configuration
- **LLM Provider**: Configure Google Gemini API
- **Content Filters**: Age range and safety settings
- **Generation Limits**: Retry and concurrency controls
- **Defaults**: Set preferred formats and styles

## 📚 API Documentation

### Core Endpoints

**Stories:**
- `POST /api/stories/generate` - Create new story (starts async generation)
- `GET /api/stories` - List stories (pagination, filtering, search)
- `GET /api/stories/:id` - Get specific story
- `GET /api/stories/:id/status` - Get generation status
- `DELETE /api/stories/:id` - Delete story

**Settings:**
- `GET /api/settings` - Get application settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/reset` - Reset to defaults

**System:**
- `GET /health` - Health check
- `GET /` - API information

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔧 Development

### Backend Development

```bash
cd backend

# Run API server
poetry run python main.py

# Run Celery worker
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info

# Run tests
poetry run pytest

# Code quality
poetry run black .
poetry run ruff check .
poetry run mypy .
```

### Frontend Development

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

### Docker Services

```bash
# Start core services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Fresh start (removes data)
docker compose down -v
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
poetry run pytest -v
```

Current test coverage focuses on:
- API endpoint integration
- Database operations
- Error handling

### Manual Testing

1. Start all services
2. Navigate to http://localhost:5173
3. Go to Settings → Add Google API key
4. Go to Generate → Create a new story
5. Monitor progress in real-time
6. View completed story in Library → Read

## 💰 Cost Estimates

Using Google Gemini (December 2024 pricing):

- **Text Generation**: ~$0.20-0.40 per story
- **Image Generation**: ~$0.45-0.55 per story (11 images)
- **Total**: ~$0.65-0.95 per 10-page illustrated storybook

For 100 stories/month: **~$65-95/month**

## 🛣️ Development Roadmap

- [x] **Phase 0**: Project Setup ✅
- [x] **Phase 1**: Core Backend & Database ✅
- [x] **Phase 2**: LLM Agent System ✅
- [x] **Phase 3**: Image Generation ✅
- [x] **Phase 4**: Frontend Development ✅
- [ ] **Phase 5**: Production Readiness (Current)
  - [ ] Performance optimization
  - [ ] Testing & code coverage
  - [ ] Documentation
  - [ ] Security hardening
  - [ ] Deployment setup
- [ ] **Phase 6**: Advanced Features
  - [ ] User accounts
  - [ ] PDF export
  - [ ] Enhanced sharing
  - [ ] Accessibility

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Guide for Claude Code instances
- **[Application Spec](specs/application-spec.md)** - Complete feature specification
- **[Development Plan](specs/development-plan.md)** - 6-phase roadmap
- **[Quick Start](QUICK_START.md)** - 5-minute setup
- **[Testing Guide](TESTING.md)** - Testing instructions
- **[Backend README](backend/README.md)** - Backend-specific docs

## ⚙️ Configuration

### Environment Variables

Backend `.env`:
```bash
# Google Gemini API
GOOGLE_API_KEY=your-api-key-here
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image

# Database & Storage
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET_NAME=storai-booker-images

# Image Settings
IMAGE_ASPECT_RATIO=16:9
COVER_ASPECT_RATIO=3:4
IMAGE_MAX_RETRIES=3
```

Frontend `.env` (optional):
```bash
VITE_API_URL=http://localhost:8000
```

## 🚨 Important Notes

### Google Gemini API
- Free tier available with rate limits
- API key required for story generation
- Safety filters may block some content

### Storage
- MinIO runs locally for development
- Images stored with 30-day signed URLs
- Total storage ~15-20MB per story

### Performance
- Story generation takes 3-5 minutes for 10 pages
- Celery worker must be running
- Frontend polls for status updates every 5 seconds

## 🤝 Contributing

This is a portfolio project currently in active development. Contributions are welcome after Phase 5 completion.

## 📝 License

Proprietary - Portfolio Project

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Icons from [Lucide](https://lucide.dev/)

---

**Version**: Phase 4 Complete
**Last Updated**: 2025-12-16
**Status**: MVP Ready, Production Hardening in Progress
