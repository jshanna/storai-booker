# 📚 StorAI-Booker

AI-powered storybook and comic book generation application using Large Language Models.

## 🎯 Project Status: Phase 1 Complete

**Current Phase:** Phase 1 - Core Backend & Database ✅
**Next Phase:** Phase 2 - LLM Agent System

### Implementation Status

**✅ Completed (Phase 0 & 1):**
- Project structure and infrastructure setup
- Docker Compose configuration (MongoDB, Redis, MinIO)
- FastAPI backend with async/await support
- MongoDB integration with Beanie ODM
- Complete REST API for story management
- Settings management system
- Request validation and error handling
- Storage service (S3/MinIO integration)
- Comprehensive test suite (14/14 tests passing)
- API documentation (Swagger & ReDoc)

**⏳ In Progress (Phase 2+):**
- LLM provider integration (OpenAI, Anthropic, Google Gemini)
- Multi-agent story generation system
- Actual story generation (currently returns mock data)
- Image generation pipeline
- Celery job queue for concurrent processing
- Frontend development
- Comic book generation

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.10+ with FastAPI
- MongoDB (Beanie ODM + Motor)
- Redis (caching & message broker)
- Celery (job queues - Phase 2)
- LangChain (AI orchestration - Phase 2)
- LLM Providers: OpenAI, Anthropic Claude, Google Gemini (Phase 2)
- Pillow (image processing - Phase 3)
- S3/MinIO (image storage)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- React Router
- React Query
- Zustand (state management)

**Infrastructure:**
- Docker + Docker Compose
- MongoDB (local or MongoDB Atlas)
- Redis (caching & message broker)
- MinIO (S3-compatible storage)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for frontend development)
- Poetry (Python dependency manager)

### Option 1: Quick Start Script (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd storai-booker

# Start services with helper script
./start-services.sh

# Setup and run backend
cd backend
poetry install
cp .env.example .env
export PATH="$HOME/.local/bin:$PATH"
poetry run python main.py
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/api/docs

### Option 2: Manual Setup

#### 1. Clone Repository

```bash
git clone <repository-url>
cd storai-booker
```

#### 2. Start Infrastructure Services

```bash
# Start MongoDB, Redis, and MinIO
docker compose up -d

# Verify services are running
docker compose ps
```

#### 3. Setup Backend Environment

```bash
cd backend

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies
poetry install

# Create environment file
cp .env.example .env
# Edit .env if needed (defaults work for local Docker setup)
```

#### 4. Run Backend

```bash
# From backend directory
poetry run python main.py

# Or activate virtual environment first
poetry shell
python main.py
```

Backend will be available at: http://localhost:8000

#### 5. Run Frontend (Optional - Basic Structure Only)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 📁 Project Structure

```
storai-booker/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   │   ├── stories.py   # Story CRUD endpoints
│   │   │   └── settings.py  # Settings management
│   │   ├── core/            # Core configuration
│   │   │   ├── config.py    # Settings & environment
│   │   │   └── database.py  # MongoDB connection
│   │   ├── models/          # Beanie ODM models
│   │   │   ├── storybook.py # Storybook document model
│   │   │   └── settings.py  # Settings document model
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic
│   │   │   └── storage.py   # S3/MinIO storage service
│   │   ├── middleware/      # Error handlers & middleware
│   │   └── utils/           # Utilities
│   ├── tests/               # Pytest test suite
│   ├── main.py              # FastAPI app entry point
│   ├── pyproject.toml       # Poetry dependencies
│   └── .env.example         # Environment variables template
│
├── frontend/                 # React TypeScript frontend (basic structure)
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── styles/          # CSS/styling
│   │   └── main.tsx         # App entry point
│   ├── package.json         # NPM dependencies
│   └── vite.config.ts       # Vite configuration
│
├── specs/                    # Project specifications
│   ├── application-spec.md  # Complete application specification
│   └── development-plan.md  # 6-phase development roadmap
│
├── docs/                     # Additional documentation
│   └── GEMINI_MODELS.md     # Google Gemini provider info
│
├── CLAUDE.md                 # Guide for Claude Code instances
├── TESTING.md                # Comprehensive testing guide
├── PHASE1_TESTING.md         # Phase 1 API testing guide
├── QUICK_START.md            # 5-minute setup guide
├── docker-compose.yml        # Docker services configuration
├── start-services.sh         # Helper script for service startup
└── test_phase1.sh            # Automated Phase 1 test script
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app

# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type check
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

# Format
npm run format
```

## 📦 Docker Services

### Available Services

- **mongodb**: MongoDB 7.0 database (port 27017)
- **redis**: Redis 7 cache & message broker (port 6379)
- **minio**: MinIO S3-compatible storage (ports 9000, 9001)
- **backend**: FastAPI application (port 8000) - profile: full
- **celery-worker**: Celery worker for async tasks - profile: full (Phase 2)
- **flower**: Celery monitoring UI (port 5555) - profile: full (Phase 2)

### Service Management

```bash
# Start core services only (MongoDB, Redis, MinIO)
docker compose up -d

# Start all services including backend (when implemented)
docker compose --profile full up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **API Docs (ReDoc)**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Frontend**: http://localhost:5173 (basic structure)

## 🧪 Testing

### Run Phase 1 Tests

```bash
# Automated test script
./test_phase1.sh

# Or manually
cd backend
poetry run pytest -v
```

**Current Test Coverage:**
- ✅ 14/14 tests passing
- ✅ Story CRUD operations
- ✅ Settings management
- ✅ Request validation
- ✅ Error handling
- ✅ Pagination and filtering

See [TESTING.md](TESTING.md) and [PHASE1_TESTING.md](PHASE1_TESTING.md) for detailed testing instructions.

## 📚 API Documentation

### Available Endpoints

**Stories:**
- `POST /api/stories/generate` - Create new story (returns pending status)
- `GET /api/stories` - List stories (pagination, filtering, search)
- `GET /api/stories/:id` - Get specific story
- `GET /api/stories/:id/status` - Get generation status
- `DELETE /api/stories/:id` - Delete story

**Settings:**
- `GET /api/settings` - Get application settings
- `PUT /api/settings` - Update settings
- `POST /api/settings/reset` - Reset to defaults

**System:**
- `GET /health` - Health check (database, storage status)
- `GET /` - API information

### Interactive Documentation

Once the backend is running:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Guide for Claude Code instances working in this repository
- **[Application Specification](specs/application-spec.md)** - Complete feature specification
- **[Development Plan](specs/development-plan.md)** - 6-phase implementation roadmap
- **[Testing Guide](TESTING.md)** - Comprehensive testing instructions
- **[Phase 1 Testing](PHASE1_TESTING.md)** - API endpoint testing guide
- **[Quick Start](QUICK_START.md)** - 5-minute setup guide
- **[Gemini Models](docs/GEMINI_MODELS.md)** - Google Gemini provider documentation

## 🛣️ Development Roadmap

- [x] **Phase 0**: Project Setup ✅
- [x] **Phase 1**: Core Backend & Database ✅
  - [x] FastAPI application structure
  - [x] MongoDB integration with Beanie ODM
  - [x] Story CRUD API endpoints
  - [x] Settings management API
  - [x] Request validation and error handling
  - [x] S3/MinIO storage service
  - [x] Test suite (14 tests)
- [ ] **Phase 2**: LLM Agent System (Next)
  - [ ] LLM provider integration (OpenAI, Anthropic, Google)
  - [ ] Coordinating agent for story planning
  - [ ] Page generation agents
  - [ ] Celery job queue setup
  - [ ] Assembly and validation logic
- [ ] **Phase 3**: Image Generation
  - [ ] Image generation service
  - [ ] Comic book panel composition
  - [ ] Speech bubble rendering
  - [ ] Image storage pipeline
- [ ] **Phase 4**: Frontend Development
  - [ ] Generation view with forms
  - [ ] Library view with filtering
  - [ ] Reader mode (storybook & comic)
  - [ ] Settings view
  - [ ] Real-time progress updates
- [ ] **Phase 5**: Production Ready
  - [ ] Performance optimization
  - [ ] Security hardening
  - [ ] Deployment setup
  - [ ] Monitoring and logging
- [ ] **Phase 6**: Advanced Features
  - [ ] User accounts
  - [ ] Export to PDF
  - [ ] Enhanced comic features
  - [ ] Accessibility improvements

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## ⚠️ Important Notes

### Phase 1 Status
- The backend API is functional and tested
- Story generation currently returns mock data (actual LLM generation in Phase 2)
- Frontend has basic structure but needs Phase 4 implementation
- Celery workers are configured but not active (Phase 2)

### Python Version
- Project originally specified Python 3.11+
- Currently compatible with Python 3.10+ for broader compatibility
- All features work correctly on Python 3.10

### MinIO Storage
- Storage service is configured but health check may show degraded
- This doesn't affect API functionality
- Bucket creation handled automatically on first startup

---

**Current Version**: Phase 1 Complete
**Last Updated**: 2025-12-14
**API Status**: Production-ready for Phase 2 development
