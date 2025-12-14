# 🧪 StorAI-Booker Testing Guide

This guide will help you test the Phase 0 MVP setup on your local machine.

## Prerequisites Checklist

Before testing, ensure you have:
- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)

## Test 1: Docker Services ✓

### Start Core Services

```bash
# Navigate to project root
cd storai-booker

# Start MongoDB, Redis, and MinIO
docker compose up -d

# Check service status
docker compose ps
```

**Expected Output:**
```
NAME                  STATUS         PORTS
storai-mongodb        Up (healthy)   27017
storai-redis          Up (healthy)   6379
storai-minio          Up (healthy)   9000, 9001
storai-minio-setup    Exited (0)
```

### Verify Services

#### 1. MongoDB
```bash
# Test MongoDB connection
docker exec -it storai-mongodb mongosh --eval "db.adminCommand('ping')"
```
**Expected:** `{ ok: 1 }`

#### 2. Redis
```bash
# Test Redis connection
docker exec -it storai-redis redis-cli ping
```
**Expected:** `PONG`

#### 3. MinIO
Open browser to: http://localhost:9001
- **Username:** minioadmin
- **Password:** minioadmin
- **Expected:** MinIO console should load
- **Verify:** `storai-booker-images` bucket exists

### View Service Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f mongodb
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v
```

## Test 2: Backend (Python + FastAPI) ✓

### Install Dependencies

```bash
cd backend

# Install dependencies with Poetry
poetry install

# Verify installation
poetry show
```

**Expected:** List of installed packages including:
- fastapi
- uvicorn
- motor
- beanie
- pydantic
- celery

### Create Local Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and set (optional for basic testing):
# - OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY
# - Other values can use defaults
```

### Run Backend Server

```bash
# Activate Poetry virtual environment
poetry shell

# Run with Python
python main.py

# OR run with uvicorn directly
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Connected to MongoDB at mongodb://localhost:27017
INFO:     Beanie ODM initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test Backend Endpoints

Open your browser or use `curl`:

#### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Expected:**
```json
{
  "status": "healthy",
  "app": "StorAI-Booker",
  "version": "0.1.0",
  "environment": "development"
}
```

#### 2. API Documentation
- Open: http://localhost:8000/api/docs
- **Expected:** Swagger UI interface loads

#### 3. Alternative API Docs
- Open: http://localhost:8000/api/redoc
- **Expected:** ReDoc interface loads

#### 4. OpenAPI Schema
```bash
curl http://localhost:8000/api/openapi.json
```
**Expected:** JSON schema with API definition

### Test Backend Code Quality

```bash
# Run linter
poetry run ruff check .

# Run formatter
poetry run black --check .

# Run type checker
poetry run mypy .
```

**Expected:** No errors (warnings are okay for now)

### Test Database Connection

```bash
# In Poetry shell
python -c "from app.core.database import db; import asyncio; asyncio.run(db.connect_db())"
```

**Expected:**
```
Connected to MongoDB at mongodb://localhost:27017
Beanie ODM initialized successfully
```

## Test 3: Frontend (React + TypeScript) ✓

### Install Dependencies

```bash
cd frontend

# Install npm packages
npm install

# Verify installation
npm list --depth=0
```

**Expected:** List of packages including:
- react
- react-dom
- react-router-dom
- vite
- typescript

### Run Development Server

```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

### Test Frontend in Browser

1. **Open:** http://localhost:5173
2. **Expected:**
   - Page loads with "📚 StorAI-Booker" header
   - "AI-Powered Storybook Generation - MVP" subtitle
   - Welcome message
   - Navigation links work:
     - `/generate` - Shows "Generate Story" page
     - `/library` - Shows "Story Library" page
     - `/settings` - Shows "Settings" page

### Test Frontend Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

**Expected:**
- Build completes without errors
- Preview server starts on http://localhost:4173

### Test Code Quality

```bash
# Run linter
npm run lint

# Run formatter
npm run format
```

**Expected:** No errors

## Test 4: Full Stack Integration ✓

### Start Everything

**Terminal 1 - Docker Services:**
```bash
docker compose up -d
docker compose logs -f
```

**Terminal 2 - Backend:**
```bash
cd backend
poetry shell
python main.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Verify Integration

1. **Frontend:** http://localhost:5173
2. **Backend API:** http://localhost:8000/health
3. **API Docs:** http://localhost:8000/api/docs
4. **MinIO:** http://localhost:9001

### Test API Proxy

The frontend is configured to proxy `/api/*` requests to the backend.

From browser console (http://localhost:5173):
```javascript
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
```

**Expected:** Health check response from backend

## Test 5: Docker Full Stack (Optional) ✓

### Build and Run Everything in Docker

```bash
# Start all services including backend
docker compose --profile full up -d --build

# Check all services
docker compose ps
```

**Expected Services:**
- mongodb
- redis
- minio
- backend (new)
- celery-worker (new)
- flower (new)

### Access Dockerized Services

- **Backend:** http://localhost:8000/api/docs
- **Frontend:** http://localhost:5173 (still run locally)
- **Flower:** http://localhost:5555

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Celery worker
docker compose logs -f celery-worker
```

## Common Issues & Solutions

### Issue: "Cannot connect to MongoDB"

**Solution:**
```bash
# Check MongoDB is running
docker compose ps mongodb

# Check MongoDB logs
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 python main.py
```

### Issue: "Poetry command not found"

**Solution:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: "npm install fails"

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: "ModuleNotFoundError in Python"

**Solution:**
```bash
cd backend

# Ensure Poetry shell is active
poetry shell

# Reinstall dependencies
poetry install --no-cache
```

## Verification Checklist

After testing, verify:

- [ ] MongoDB is running and accessible
- [ ] Redis is running and accessible
- [ ] MinIO is running with bucket created
- [ ] Backend starts without errors
- [ ] Backend health endpoint responds
- [ ] Backend API docs are accessible
- [ ] Frontend starts without errors
- [ ] Frontend pages load and navigate
- [ ] Frontend can call backend API
- [ ] No console errors in browser
- [ ] No Python errors in backend logs

## Next Steps

Once all tests pass:

1. ✅ Phase 0 is verified and working
2. 📝 Ready to begin Phase 1: Core Backend & Database
3. 🚀 Start implementing API endpoints and services

## Cleanup

```bash
# Stop all services
docker compose down

# Remove volumes (fresh start next time)
docker compose down -v

# Exit Poetry shell
exit

# Stop frontend dev server
Ctrl+C
```

---

**Testing Status:**
- Phase 0 Setup: ✅ Ready to test
- All dependencies configured: ✅
- Docker compose ready: ✅
- Project structure complete: ✅

**Estimated Testing Time:** 15-20 minutes
