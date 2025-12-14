# 📚 StorAI-Booker

AI-powered storybook and comic book generation application using Large Language Models.

## 🎯 Project Status: MVP Development

**Current Phase:** Phase 0 - Project Setup ✅
**Next Phase:** Phase 1 - Core Backend & Database

### MVP Features
- ✅ Traditional storybook generation
- ✅ Library view and management
- ✅ Basic reader mode
- ✅ LLM provider configuration
- ⏳ Comic book generation (Post-MVP)

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- MongoDB (Beanie ODM + Motor)
- Celery + Redis (job queues)
- LangChain (AI orchestration)
- Pillow (image processing)
- S3/MinIO (image storage)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- React Router
- React Query
- Zustand (state management)

**Infrastructure:**
- Docker + Docker Compose
- MongoDB Atlas / self-hosted
- Redis (caching & message broker)
- MinIO (S3-compatible storage)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- Poetry (Python dependency manager)

### 1. Clone Repository

```bash
git clone <repository-url>
cd storai-booker
```

### 2. Setup Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your API keys
```

### 3. Start Services with Docker

```bash
# Start MongoDB, Redis, and MinIO only
docker-compose up -d

# Or start everything including backend and Celery workers
docker-compose --profile full up -d
```

### 4. Run Backend (Local Development)

```bash
cd backend

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Run FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/api/docs

### 5. Run Frontend (Local Development)

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
│   │   ├── api/             # API routes
│   │   ├── core/            # Core configuration
│   │   ├── models/          # Beanie ODM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic & agents
│   │   └── utils/           # Utilities
│   ├── tests/               # Tests
│   ├── main.py              # FastAPI app entry
│   ├── pyproject.toml       # Poetry dependencies
│   └── Dockerfile           # Backend Docker image
│
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── store/           # Zustand stores
│   │   ├── types/           # TypeScript types
│   │   └── styles/          # CSS/styling
│   ├── package.json         # NPM dependencies
│   └── vite.config.ts       # Vite configuration
│
├── specs/                    # Project specifications
│   ├── application-spec.md  # Application specification
│   └── development-plan.md  # Development roadmap
│
├── docker-compose.yml        # Docker services
└── README.md                 # This file
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Run tests
poetry run pytest

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
- **redis**: Redis cache & message broker (port 6379)
- **minio**: S3-compatible object storage (ports 9000, 9001)
- **backend**: FastAPI application (port 8000) - profile: full
- **celery-worker**: Celery worker for async tasks - profile: full
- **flower**: Celery monitoring UI (port 5555) - profile: full

### Service Management

```bash
# Start core services only (MongoDB, Redis, MinIO)
docker-compose up -d

# Start all services including backend
docker-compose --profile full up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **Flower Dashboard**: http://localhost:5555 (when running full profile)
- **Frontend**: http://localhost:5173

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## 📖 Documentation

- [Application Specification](specs/application-spec.md)
- [Development Plan](specs/development-plan.md)

## 🛣️ Development Roadmap

- [x] **Phase 0**: Project Setup ✅
- [ ] **Phase 1**: Core Backend & Database (Weeks 2-4)
- [ ] **Phase 2**: LLM Agent System (Weeks 5-7)
- [ ] **Phase 3**: Image Generation (Weeks 8-10)
- [ ] **Phase 4**: Frontend Development (Weeks 11-15)
- [ ] **Phase 5**: Production Ready (Weeks 16-18)
- [ ] **Phase 6**: Advanced Features (Weeks 19-24+)

---

**MVP Timeline**: 18 weeks
**Full Version Timeline**: 24-32 weeks
