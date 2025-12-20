# Quick Start Guide

Get StorAI-Booker running in minutes!

## Option 1: Docker Compose (Recommended)

The fastest way to get everything running.

### Prerequisites

- Docker & Docker Compose v24.0+ ([Install Docker](https://docs.docker.com/get-docker/))
- Google API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Steps

```bash
# 1. Clone repository
git clone <repository-url>
cd storai-booker

# 2. Configure environment
cp .env.production.example .env.production

# 3. Edit .env.production with your settings:
#    - GOOGLE_API_KEY (required for story generation)
#    - Change MINIO_ROOT_PASSWORD (security)
#    - Change SECRET_KEY and JWT_SECRET_KEY (security)

# 4. Start all services
docker compose up -d

# 5. Wait for services to be healthy (about 1 minute)
docker compose ps

# 6. Open browser
open http://localhost
```

### Verify It Works

```bash
# All services should show "healthy"
docker compose ps

# Test API
curl http://localhost:8000/health

# View logs
docker compose logs -f
```

### Access Points

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost | Main application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| MinIO Console | http://localhost:9001 | Storage admin |

### Stop Services

```bash
docker compose down        # Stop services (keeps data)
docker compose down -v     # Stop and remove all data
```

---

## Option 2: Local Development

For development with hot-reload and debugging.

### Prerequisites

- Docker & Docker Compose (for MongoDB, Redis, MinIO)
- Python 3.10+ with Poetry
- Node.js 18+ with npm
- Google API Key

### Steps

```bash
# 1. Start infrastructure only
docker compose up -d mongodb redis minio createbuckets

# 2. Setup backend
cd backend
poetry install
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 3. Run backend (new terminal)
cd backend
poetry run python main.py

# 4. Run Celery worker (new terminal)
cd backend
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info

# 5. Setup and run frontend (new terminal)
cd frontend
npm install
npm run dev

# 6. Open browser
open http://localhost:5173
```

### Access Points (Development)

| Service | URL |
|---------|-----|
| Frontend (Vite) | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| MinIO Console | http://localhost:9001 |

### Stop Development

```bash
# Stop frontend: Ctrl+C in frontend terminal
# Stop backend: Ctrl+C in backend terminal
# Stop Celery: Ctrl+C in celery terminal
# Stop Docker infrastructure:
docker compose down
```

---

## Troubleshooting

### Docker services won't start

```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :8000

# Remove everything and start fresh
docker compose down -v
docker compose up -d
```

### Backend errors

```bash
# View backend logs
docker compose logs backend

# Or for local development:
cd backend
poetry install --no-cache
poetry run python main.py
```

### Story generation not working

1. Check your Google API key is set in `.env.production` or `.env`
2. Check Celery worker is running:
   ```bash
   docker compose logs celery-worker
   ```
3. Test API key in Settings page

### Frontend not loading

```bash
# View frontend logs
docker compose logs frontend

# Check nginx is proxying correctly
curl http://localhost/api/health
```

### Out of disk space

```bash
# Check disk usage
docker system df

# Clean up unused Docker resources
docker system prune -a
```

---

## Next Steps

1. **Create an account** at http://localhost
2. **Configure API key** in Settings (if not set in environment)
3. **Generate your first story** in the Generate page
4. **Explore** the Browse page for public stories

## Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment details
- [Configuration Guide](docs/CONFIGURATION.md) - All environment variables
- [API Documentation](docs/API.md) - REST API reference
- [Features Guide](docs/FEATURES.md) - Complete feature documentation
