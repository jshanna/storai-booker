# StorAI-Booker Configuration Guide

Complete guide to configuring StorAI-Booker via environment variables and settings.

## Table of Contents

- [Environment Files](#environment-files)
- [Backend Configuration](#backend-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Docker Compose Variables](#docker-compose-variables)
- [Configuration Examples](#configuration-examples)
- [Security Best Practices](#security-best-practices)

## Environment Files

### Backend: `backend/.env`

Created from `backend/.env.example`:
```bash
cp backend/.env.example backend/.env
```

### Production: `.env.production`

Created from `.env.production.example`:
```bash
cp .env.production.example .env.production
```

### Frontend: `frontend/.env` (Optional)

Vite automatically proxies `/api/*` to backend, so this is usually not needed.

---

## Backend Configuration

### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | "StorAI-Booker" | Application name |
| `APP_VERSION` | string | "0.1.0" | Application version |
| `ENV` | string | "development" | Environment: `development` or `production` |
| `DEBUG` | boolean | true | Enable debug mode |
| `SECRET_KEY` | string | "dev-secret..." | Secret key for encryption (change in production!) |

**Example:**
```bash
APP_NAME=StorAI-Booker
APP_VERSION=0.1.0
ENV=production
DEBUG=false
SECRET_KEY=your-very-long-random-secret-key-here
```

**Secret Key Generation:**
```bash
# Generate strong secret key
openssl rand -base64 32
```

---

### Server Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | "0.0.0.0" | Server bind address |
| `PORT` | integer | 8000 | Server port |

**Example:**
```bash
HOST=0.0.0.0
PORT=8000
```

---

### Database Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MONGODB_URL` | string | "mongodb://localhost:27017" | MongoDB connection string |
| `MONGODB_DB_NAME` | string | "storai_booker" | Database name |

**Example:**
```bash
# Local development
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=storai_booker

# Production with authentication
MONGODB_URL=mongodb://user:password@mongodb-host:27017/storai_booker?authSource=admin
MONGODB_DB_NAME=storai_booker

# MongoDB Atlas
MONGODB_URL=mongodb+srv://user:password@cluster0.mongodb.net/storai_booker?retryWrites=true&w=majority
```

---

### Redis Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | string | "redis://localhost:6379/0" | Redis cache connection |
| `CELERY_BROKER_URL` | string | "redis://localhost:6379/1" | Celery broker |
| `CELERY_RESULT_BACKEND` | string | "redis://localhost:6379/2" | Celery result backend |

**Example:**
```bash
# Local development
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Production with password
REDIS_URL=redis://:password@redis-host:6379/0
CELERY_BROKER_URL=redis://:password@redis-host:6379/1
CELERY_RESULT_BACKEND=redis://:password@redis-host:6379/2
```

---

### Storage Settings (MinIO/S3)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `S3_ENDPOINT_URL` | string | null | MinIO/S3 endpoint (omit for AWS S3) |
| `S3_PUBLIC_URL` | string | null | Public URL for image access |
| `S3_ACCESS_KEY_ID` | string | "" | S3/MinIO access key |
| `S3_SECRET_ACCESS_KEY` | string | "" | S3/MinIO secret key |
| `S3_BUCKET_NAME` | string | "storai-booker-images" | Bucket name |
| `S3_REGION` | string | "us-east-1" | AWS region |

**Example (MinIO - Development):**
```bash
S3_ENDPOINT_URL=http://localhost:9000
S3_PUBLIC_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=storai-booker-images
S3_REGION=us-east-1
```

**Example (AWS S3 - Production):**
```bash
# S3_ENDPOINT_URL is not set (use AWS default)
S3_PUBLIC_URL=https://s3.us-east-1.amazonaws.com
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=my-storai-production-bucket
S3_REGION=us-east-1
```

**Example (MinIO - Production):**
```bash
S3_ENDPOINT_URL=https://minio.example.com
S3_PUBLIC_URL=https://minio.example.com
S3_ACCESS_KEY_ID=your-minio-access-key
S3_SECRET_ACCESS_KEY=your-minio-secret-key
S3_BUCKET_NAME=storai-booker-images
S3_REGION=us-east-1
```

**S3_PUBLIC_URL Notes:**
- Used for constructing public image URLs
- For AWS S3: `https://s3.{region}.amazonaws.com`
- For MinIO: same as `S3_ENDPOINT_URL`
- Must be accessible from frontend clients

---

### LLM Provider Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GOOGLE_API_KEY` | string | "" | Google AI API key |
| `OPENAI_API_KEY` | string | "" | OpenAI API key (optional) |
| `ANTHROPIC_API_KEY` | string | "" | Anthropic API key (optional) |
| `DEFAULT_LLM_PROVIDER` | string | "google" | Default provider: `google`, `openai`, or `anthropic` |
| `DEFAULT_TEXT_MODEL` | string | "gemini-2.5-flash" | Default text generation model |
| `DEFAULT_IMAGE_MODEL` | string | "gemini-2.5-flash-image" | Default image generation model |

**Example:**
```bash
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image
```

**Supported Models:**

**Google (Recommended):**
- Text: `gemini-2.5-flash`, `gemini-2.0-flash-exp`
- Image: `gemini-2.5-flash-image`, `gemini-2.0-flash-exp`

**OpenAI:**
- Text: `gpt-4-turbo-preview`, `gpt-3.5-turbo`
- Image: `dall-e-3`

**Anthropic:**
- Text: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Image: Not supported (requires Google or OpenAI for images)

**API Key Security:**
- API keys are encrypted at rest using Fernet encryption
- Never commit API keys to Git
- Use environment variables or secrets management

---

### Image Generation Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `IMAGE_ASPECT_RATIO` | string | "16:9" | Page illustration aspect ratio |
| `COVER_ASPECT_RATIO` | string | "3:4" | Cover image aspect ratio |
| `IMAGE_MAX_RETRIES` | integer | 3 | Max retries for failed image generation |
| `IMAGE_GENERATION_TIMEOUT` | integer | 60 | Timeout in seconds per image |
| `COVER_FONT_PATH` | string | null | Custom font path for cover text |

**Example:**
```bash
IMAGE_ASPECT_RATIO=16:9
COVER_ASPECT_RATIO=3:4
IMAGE_MAX_RETRIES=3
IMAGE_GENERATION_TIMEOUT=60
COVER_FONT_PATH=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
```

**Aspect Ratios:**
- `16:9` - Widescreen (horizontal)
- `3:4` - Portrait (vertical, good for covers)
- `1:1` - Square
- `4:3` - Standard horizontal

---

### Story Generation Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEFAULT_AGE_MIN` | integer | 3 | Minimum allowed audience age |
| `DEFAULT_AGE_MAX` | integer | 12 | Maximum allowed audience age |
| `DEFAULT_RETRY_LIMIT` | integer | 3 | Max retries for failed page generation |
| `DEFAULT_MAX_CONCURRENT_PAGES` | integer | 5 | Max parallel page generations |
| `NSFW_FILTER_ENABLED` | boolean | true | Enable NSFW content filtering |

**Example:**
```bash
DEFAULT_AGE_MIN=3
DEFAULT_AGE_MAX=12
DEFAULT_RETRY_LIMIT=3
DEFAULT_MAX_CONCURRENT_PAGES=5
NSFW_FILTER_ENABLED=true
```

**Performance Notes:**
- Higher `MAX_CONCURRENT_PAGES` = faster generation but more memory
- Lower values reduce memory usage but slow generation
- Recommended: 3-5 for development, 5-8 for production

---

### CORS Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ORIGINS` | string list | ["http://localhost:3000", "http://localhost:5173"] | Allowed frontend origins |
| `CORS_CREDENTIALS` | boolean | true | Allow credentials in CORS |

**Example:**
```bash
# Development
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Production
CORS_ORIGINS=["https://storai.example.com"]

# Multiple domains
CORS_ORIGINS=["https://app.example.com", "https://admin.example.com"]
```

---

### Security Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMIT_PER_MINUTE` | integer | 100 | Max requests per minute per IP |

**Example:**
```bash
# Development (lenient)
RATE_LIMIT_PER_MINUTE=200

# Production (strict)
RATE_LIMIT_PER_MINUTE=60
```

---

### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | "INFO" | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | string | "json" | Log format: `json` or `text` |

**Example:**
```bash
# Development (human-readable)
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Production (structured, machine-parseable)
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Log Levels:**
- `DEBUG`: Verbose (all logs including debug info)
- `INFO`: Standard (request/response, operations)
- `WARNING`: Issues that don't prevent operation
- `ERROR`: Errors that need attention

---

## Frontend Configuration

### `frontend/.env` (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_API_URL` | string | "" | Backend API URL (usually not needed) |

**Example:**
```bash
# Usually not needed (Vite proxy configured)
# VITE_API_URL=http://localhost:8000

# Custom backend URL
VITE_API_URL=https://api.storai.example.com
```

**Vite Proxy (Default):**

The frontend `vite.config.ts` proxies `/api/*` to `http://localhost:8000`, so you typically don't need to set `VITE_API_URL` for development.

---

## Docker Compose Variables

### `.env.production` (Production Deployment)

Used by `docker-compose.prod.yml`:

```bash
# Required: LLM Provider API Key
GOOGLE_API_KEY=your_actual_google_api_key_here

# Required: MinIO Credentials (change defaults!)
MINIO_ROOT_USER=your_minio_admin_user
MINIO_ROOT_PASSWORD=your_strong_random_password_here

# Optional: Other providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# LLM Defaults
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image

# Storage
S3_BUCKET_NAME=storai-booker-images
```

**Security Warning:**

**DO NOT** commit `.env.production` to Git! It contains sensitive credentials.

---

## Configuration Examples

### Local Development Setup

**`backend/.env`:**
```bash
# Application
ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Server
HOST=0.0.0.0
PORT=8000

# Database & Cache (Docker services)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=storai_booker
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Storage (MinIO via Docker)
S3_ENDPOINT_URL=http://localhost:9000
S3_PUBLIC_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=storai-booker-images
S3_REGION=us-east-1

# LLM Provider
GOOGLE_API_KEY=AIzaSy...  # Your actual API key
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image

# Image Settings
IMAGE_ASPECT_RATIO=16:9
COVER_ASPECT_RATIO=3:4
IMAGE_MAX_RETRIES=3

# Story Defaults
DEFAULT_AGE_MIN=3
DEFAULT_AGE_MAX=12
DEFAULT_RETRY_LIMIT=3
DEFAULT_MAX_CONCURRENT_PAGES=5
NSFW_FILTER_ENABLED=true

# CORS (Frontend URLs)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=200

# Logging (development: human-readable)
LOG_LEVEL=INFO
LOG_FORMAT=text
```

---

### Production Docker Deployment

**`.env.production`:**
```bash
# LLM API Keys
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...

# MinIO Credentials (CHANGE THESE!)
MINIO_ROOT_USER=admin-user-2024
MINIO_ROOT_PASSWORD=v3rY-$tr0ng-p@ssw0rd-h3r3

# Defaults
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image

# Storage
S3_BUCKET_NAME=storai-production-images
```

**Backend runs with these variables (set by compose):**
- `ENV=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `LOG_FORMAT=json` (structured logging)
- `RATE_LIMIT_PER_MINUTE=60` (stricter limits)

---

### AWS S3 Production Setup

**`backend/.env`:**
```bash
ENV=production
DEBUG=false
SECRET_KEY=$(openssl rand -base64 32)  # Generate this!

# AWS RDS MongoDB (or Atlas)
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/storai?retryWrites=true

# AWS ElastiCache Redis
REDIS_URL=redis://my-elasticache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://my-elasticache.amazonaws.com:6379/1
CELERY_RESULT_BACKEND=redis://my-elasticache.amazonaws.com:6379/2

# AWS S3
# S3_ENDPOINT_URL not set (use AWS default)
S3_PUBLIC_URL=https://s3.us-east-1.amazonaws.com
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY
S3_BUCKET_NAME=storai-prod-images
S3_REGION=us-east-1

# LLM
GOOGLE_API_KEY=AIzaSy...

# CORS (production domain)
CORS_ORIGINS=["https://storai.example.com"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=60
```

---

## Security Best Practices

### 1. Secret Key

**Generate Strong Key:**
```bash
openssl rand -base64 32
```

**Never Use Defaults in Production:**
```bash
# Bad
SECRET_KEY=dev-secret-key-change-in-production

# Good
SECRET_KEY=YOUR_SECRET_KEY_HERE
```

### 2. API Keys

**Protection:**
- Store in `.env` files only
- Never commit to Git
- Rotate periodically
- Use read-only keys where possible
- Monitor usage for anomalies

**Environment-Specific Keys:**
```bash
# Development
GOOGLE_API_KEY=dev-key-with-quotas

# Production
GOOGLE_API_KEY=prod-key-with-higher-limits
```

### 3. Database Credentials

**MongoDB:**
```bash
# Bad
MONGODB_URL=mongodb://localhost:27017

# Good (production)
MONGODB_URL=mongodb://user:strong-password@host:27017/storai?authSource=admin
```

**Redis:**
```bash
# Bad
REDIS_URL=redis://localhost:6379/0

# Good (production)
REDIS_URL=redis://:strong-redis-password@host:6379/0
```

### 4. Storage Credentials

**MinIO/S3:**
```bash
# Bad (default MinIO)
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin

# Good (production)
S3_ACCESS_KEY_ID=admin-$(openssl rand -hex 8)
S3_SECRET_ACCESS_KEY=$(openssl rand -base64 32)
```

### 5. CORS Configuration

**Development:**
```bash
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

**Production (Strict):**
```bash
CORS_ORIGINS=["https://storai.example.com"]
# Never use "*" in production!
```

### 6. Rate Limiting

**Adjust Based on Traffic:**
```bash
# Development: lenient
RATE_LIMIT_PER_MINUTE=200

# Production: strict
RATE_LIMIT_PER_MINUTE=60

# High-traffic production
RATE_LIMIT_PER_MINUTE=100
```

### 7. Environment File Permissions

```bash
# Restrict access to .env files
chmod 600 backend/.env
chmod 600 .env.production

# Verify
ls -la backend/.env  # Should show: -rw-------
```

### 8. Git Ignore

Ensure `.gitignore` includes:
```
.env
.env.production
.env.local
.env.*.local
*.key
*.pem
```

---

## Troubleshooting

### "API key not set" error

**Check:**
```bash
# Backend .env file exists
ls backend/.env

# Key is set
grep GOOGLE_API_KEY backend/.env

# No trailing spaces or quotes
cat backend/.env | grep GOOGLE_API_KEY
```

### "Connection refused" errors

**MongoDB:**
```bash
# Check MongoDB is running
docker ps | grep mongo

# Test connection
docker exec -it storai-mongodb mongosh
```

**Redis:**
```bash
# Check Redis is running
docker ps | grep redis

# Test connection
docker exec -it storai-redis redis-cli ping
```

### "S3 Upload Failed" errors

**Check MinIO:**
```bash
# MinIO running
docker ps | grep minio

# Access console
open http://localhost:9001

# Check bucket exists
# Login with MINIO_ROOT_USER/PASSWORD
```

### Configuration not loading

**Restart services after .env changes:**
```bash
# Backend
# Stop uvicorn/main.py and restart

# Celery worker
# Stop celery worker and restart

# Docker
docker compose restart backend celery-worker
```

---

**Last Updated**: 2025-12-17
**Version**: Phase 5
