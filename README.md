# StorAI-Booker

AI-powered storybook and comic book generation application using Google Gemini for creating personalized, illustrated children's stories.

![Project Status](https://img.shields.io/badge/Status-Phase%206%20In%20Progress-blue)
![License](https://img.shields.io/badge/License-Proprietary-blue)

## Project Status

**Current Phase:** Phase 6 - Advanced Features (In Progress)

### What's Working

**Full-Stack Application**
- Complete React/TypeScript frontend with modern UI
- Full backend API with Google Gemini integration
- End-to-end story and comic book generation pipeline
- User authentication (email/password + Google/GitHub OAuth)
- Real-time generation progress tracking

**Story Generation**
- AI-powered story planning and writing
- Traditional storybooks and comic books
- Character description expansion and consistency
- Age-appropriate content validation (ages 3-12)
- Automatic illustration generation with character reference sheets
- Custom cover images with titles

**User Features**
- User accounts with profile management
- Personal story library with search, filter, and sort
- Story sharing with public links
- Comments on shared stories
- Bookmark/save other users' stories
- Browse public stories from the community

**Export Options**
- PDF document export
- EPUB e-book format
- CBZ comic book format
- ZIP archive of images

**Production Features**
- Sentry error tracking integration
- Response caching with Redis
- Rate limiting and security headers
- Structured JSON logging with correlation IDs
- CI/CD with GitHub Actions
- Docker Compose deployment

## Quick Start

### Prerequisites

- **Docker & Docker Compose** v24.0+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Google API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### Deploy with Docker Compose

```bash
# 1. Clone repository
git clone <repository-url>
cd storai-booker

# 2. Configure environment
cp .env.production.example .env.production
# Edit .env.production - add your GOOGLE_API_KEY and change default passwords

# 3. Start all services
docker compose up -d

# 4. Open browser
open http://localhost
```

That's it! The application is now running with all services containerized.

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| API Docs (ReDoc) | http://localhost:8000/api/redoc |
| MinIO Console | http://localhost:9001 |

### Verify Deployment

```bash
# Check all services are healthy
docker compose ps

# View logs
docker compose logs -f

# Test health endpoint
curl http://localhost:8000/health
```

### Development Mode (Optional)

For local development with hot-reload, see [QUICK_START.md](QUICK_START.md).

## Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- shadcn/ui component library
- React Query (server state)
- Zustand (client state)
- React Hook Form + Zod validation
- Tailwind CSS
- Sentry (error tracking)

**Backend:**
- Python 3.10+ with FastAPI
- MongoDB (Beanie ODM + Motor)
- Redis (caching & Celery broker)
- Celery (async task queue)
- Google Gemini (text & image generation)
- Pillow (image processing)
- MinIO (S3-compatible storage)
- Sentry (error tracking)

**Infrastructure:**
- Docker + Docker Compose
- MongoDB 7.0
- Redis 7
- MinIO (local S3)
- GitHub Actions (CI/CD)

### Project Structure

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
│   │   │   ├── image/      # Image generation
│   │   │   ├── llm/        # LLM provider integration
│   │   │   ├── export/     # PDF, EPUB, CBZ exporters
│   │   │   └── ...
│   │   ├── tasks/          # Celery background tasks
│   │   └── middleware/     # Security, logging, errors
│   ├── tests/              # Pytest test suite
│   └── main.py             # FastAPI entry point
│
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── lib/
│   │   │   ├── api/        # API client
│   │   │   ├── hooks/      # React hooks
│   │   │   └── stores/     # Zustand stores
│   │   └── types/          # TypeScript types
│   └── package.json
│
├── docs/                    # Documentation
├── specs/                   # Project specifications
└── docker-compose.yml       # Infrastructure services
```

## Features

### Story Generation
- **Personalized Stories**: Age-appropriate content (3-12 years)
- **Two Formats**: Traditional storybooks and comic books
- **Character Consistency**: Reference sheets for visual consistency
- **Multiple Styles**: Watercolor, digital art, cartoon, anime, and more
- **Flexible Length**: 5-20 pages per story
- **Smart Validation**: Automatic quality and coherence checking

### User Accounts
- Email/password registration and login
- OAuth with Google and GitHub
- Profile management with avatar
- Secure password change

### Library & Discovery
- Personal library with all your stories
- Search by title
- Filter by format (storybook/comic), status, sharing
- Browse public stories from other users
- Save/bookmark stories for later

### Story Sharing
- Share stories with a unique public link
- Toggle sharing on/off anytime
- Comments on shared stories
- Owner can view and manage comments

### Export Options
- **PDF**: Best for printing and reading on any device
- **EPUB**: For e-readers like Kindle, Kobo, or Apple Books
- **CBZ**: Comic book format for comic reader apps
- **Images**: Download all images as a ZIP archive

### Templates
- Pre-made story templates for quick starts
- Genre-specific templates (adventure, fantasy, etc.)
- Character template suggestions

## API Documentation

### Core Endpoints

**Authentication:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `GET /api/auth/google/authorize` - Google OAuth
- `GET /api/auth/github/authorize` - GitHub OAuth

**Stories:**
- `POST /api/stories/generate` - Create new story
- `GET /api/stories` - List user's stories
- `GET /api/stories/:id` - Get specific story
- `DELETE /api/stories/:id` - Delete story

**Sharing:**
- `POST /api/stories/:id/share` - Enable sharing
- `DELETE /api/stories/:id/share` - Disable sharing
- `GET /api/shared` - List public stories
- `GET /api/shared/:token` - View shared story

**Bookmarks:**
- `GET /api/bookmarks` - List user's bookmarks
- `POST /api/bookmarks/:story_id` - Add bookmark
- `DELETE /api/bookmarks/:story_id` - Remove bookmark

**Comments:**
- `GET /api/stories/:id/comments` - List comments
- `POST /api/stories/:id/comments` - Add comment
- `DELETE /api/comments/:id` - Delete comment

**Exports:**
- `GET /api/exports/:id/pdf` - Export as PDF
- `GET /api/exports/:id/epub` - Export as EPUB
- `GET /api/exports/:id/cbz` - Export as CBZ
- `GET /api/exports/:id/images` - Export images as ZIP

**Templates:**
- `GET /api/templates` - List available templates
- `GET /api/templates/:id` - Get template details

**Settings:**
- `GET /api/settings` - Get application settings
- `PUT /api/settings` - Update settings

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Development

### Backend Development

```bash
cd backend

# Run API server
poetry run python main.py

# Run Celery worker
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app

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

# Type check
npm run typecheck
```

### Docker Services

```bash
# Start core services
docker compose up -d

# Start everything including backend
docker compose --profile full up -d

# View logs
docker compose logs -f [service-name]

# Stop services
docker compose down

# Fresh start (removes data)
docker compose down -v
```

## Configuration

### Backend Environment Variables

```bash
# Application
APP_NAME=StorAI-Booker
ENV=development
SECRET_KEY=your-secret-key

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=storai_booker

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Storage (MinIO/S3)
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=storai-booker-images

# Google Gemini (required)
GOOGLE_API_KEY=your-api-key
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.0-flash-exp

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# OAuth (optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret

# Sentry (optional)
SENTRY_DSN=your-sentry-dsn
SENTRY_ENVIRONMENT=development
```

### Frontend Environment Variables

```bash
# Sentry (optional)
VITE_SENTRY_DSN=your-sentry-dsn
VITE_SENTRY_ENVIRONMENT=development
VITE_APP_VERSION=0.1.0
```

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for complete configuration reference.

## Documentation

### Getting Started
- **[Quick Start](QUICK_START.md)** - 5-minute setup guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment with Docker
- **[Configuration Guide](docs/CONFIGURATION.md)** - Environment variables reference

### User Guide
- **[Features Guide](docs/FEATURES.md)** - Complete feature documentation

### API & Development
- **[API Documentation](docs/API.md)** - REST API reference
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Testing Guide](TESTING.md)** - Testing instructions

### Operations
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[CI/CD Guide](docs/CI_CD.md)** - GitHub Actions workflows

### Project Planning
- **[Application Spec](specs/application-spec.md)** - Feature specification
- **[Development Plan](specs/development-plan.md)** - Implementation roadmap

## Development Roadmap

- [x] **Phase 0**: Project Setup
- [x] **Phase 1**: Core Backend & Database
- [x] **Phase 2**: LLM Agent System
- [x] **Phase 3**: Image Generation
- [x] **Phase 4**: Frontend Development
- [x] **Phase 5**: Production Readiness
  - [x] 5.1 Testing & Code Coverage
  - [x] 5.2 Performance Optimization
  - [x] 5.3 Security Hardening
  - [x] 5.4 Error Handling & Logging (Sentry)
  - [x] 5.5 Documentation
  - [x] 5.6 CI/CD Pipeline
- [ ] **Phase 6**: Advanced Features (In Progress)
  - [x] 6.1 Enhanced Comic Features
  - [x] 6.2 Export & Sharing (PDF, EPUB, CBZ)
  - [x] 6.3 User Accounts & Authentication
  - [x] 6.4 Story Sharing & Comments
  - [x] 6.5 Templates & Themes
  - [x] 6.6 Accessibility (WCAG 2.1 AA)
  - [ ] 6.7 Internationalization

## Cost Estimates

Using Google Gemini (December 2024 pricing):

| Item | Cost per Story |
|------|---------------|
| Text Generation | ~$0.20-0.40 |
| Image Generation | ~$0.45-0.55 |
| **Total (10 pages)** | **~$0.65-0.95** |

For 100 stories/month: ~$65-95/month

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

Proprietary - Portfolio Project

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Powered by [Google Gemini](https://ai.google.dev/)
- Icons from [Lucide](https://lucide.dev/)

---

**Version**: 0.1.0
**Last Updated**: 2024-12-20
**Status**: Phase 6 In Progress
