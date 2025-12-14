# ⚡ Quick Start Guide

Get StorAI-Booker running in 5 minutes!

## 🚀 Fastest Path

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Backend (new terminal)
cd backend
cp .env.example .env
poetry install
poetry shell
python main.py

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## ✅ Verify It Works

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

## 🔍 Check Status

```bash
# Docker services
docker compose ps

# Backend logs
# (in backend terminal, should show "Application startup complete")

# Frontend logs
# (in frontend terminal, should show "Local: http://localhost:5173")
```

## ❌ Quick Troubleshooting

**Services won't start?**
```bash
docker compose down -v
docker compose up -d
```

**Backend errors?**
```bash
cd backend
poetry install --no-cache
poetry shell
python main.py
```

**Frontend errors?**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 📚 Detailed Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

## 🛑 Stop Everything

```bash
# Stop frontend: Ctrl+C in frontend terminal
# Stop backend: Ctrl+C in backend terminal
# Stop Docker: docker compose down
```
