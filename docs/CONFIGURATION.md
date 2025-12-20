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

### Frontend: `frontend/.env.local`

Created from `frontend/.env.example`:
```bash
cp frontend/.env.example frontend/.env.local
```

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

### JWT Authentication Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_SECRET_KEY` | string | auto-generated | Secret key for JWT signing |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | integer | 60 | Access token expiration in minutes |

**Example:**
```bash
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**JWT Key Generation:**
```bash
# Generate a secure JWT secret key
openssl rand -hex 32
```

**Security Notes:**
- JWT keys are auto-generated on first run if not set
- Always set explicit keys in production
- Rotate keys periodically for security

---

### OAuth Provider Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GOOGLE_CLIENT_ID` | string | "" | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | string | "" | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | string | "" | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | string | "" | GitHub OAuth client secret |
| `OAUTH_REDIRECT_BASE_URL` | string | "http://localhost:5173" | Base URL for OAuth redirects |

**Example:**
```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OAuth redirect URL (frontend)
OAUTH_REDIRECT_BASE_URL=https://storai.example.com
```

**Setting Up OAuth:**

**Google:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to APIs & Services > Credentials
4. Create OAuth 2.0 Client ID (Web application)
5. Add authorized redirect URI: `{BACKEND_URL}/api/auth/google/callback`
6. Copy Client ID and Client Secret

**GitHub:**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set Authorization callback URL: `{BACKEND_URL}/api/auth/github/callback`
4. Copy Client ID and generate Client Secret

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

### Sentry Error Tracking Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SENTRY_DSN` | string | "" | Sentry Data Source Name (leave empty to disable) |
| `SENTRY_ENVIRONMENT` | string | "development" | Environment name in Sentry |
| `SENTRY_TRACES_SAMPLE_RATE` | float | 0.1 | Performance monitoring sample rate (0.0 to 1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | float | 0.1 | Profiling sample rate (0.0 to 1.0) |

**Example:**
```bash
# Production with Sentry
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/1234567
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Development (disable Sentry)
SENTRY_DSN=
```

**Setting Up Sentry:**

1. Create a free account at [sentry.io](https://sentry.io)
2. Create a new project (Python/FastAPI for backend, React for frontend)
3. Copy the DSN from Project Settings > Client Keys
4. Add DSN to your environment variables

**Sample Rate Guidelines:**
- `0.0`: Disabled (no performance data sent)
- `0.1`: 10% sampling (recommended for production)
- `1.0`: 100% sampling (recommended for development/staging)

**Features Enabled:**
- Error tracking with stack traces
- Performance monitoring (request timing)
- Session replay (frontend only)
- Release tracking
- User context (when logged in)

**Sensitive Data:**
- Sensitive headers (Authorization, Cookie) are automatically filtered
- API keys are never sent to Sentry
- User emails are included for debugging (can be disabled)

---

## Frontend Configuration

### `frontend/.env.local`

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VITE_API_URL` | string | "" | Backend API URL (usually not needed) |
| `VITE_SENTRY_DSN` | string | "" | Sentry DSN for frontend error tracking |
| `VITE_SENTRY_ENVIRONMENT` | string | "development" | Environment name in Sentry |
| `VITE_APP_VERSION` | string | "0.1.0" | Application version for releases |

**Example:**
```bash
# Sentry error tracking (optional)
VITE_SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/7654321
VITE_SENTRY_ENVIRONMENT=production
VITE_APP_VERSION=0.1.0

# Custom backend URL (usually not needed)
# VITE_API_URL=https://api.storai.example.com
```

**Vite Proxy (Default):**

The frontend `vite.config.ts` proxies `/api/*` to `http://localhost:8000`, so you typically don't need to set `VITE_API_URL` for development.

---

## Docker Compose Variables

### `.env.production` (Production Deployment)

Used by `docker-compose.yml`:

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

# Authentication
JWT_SECRET_KEY=your-production-jwt-secret

# OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Sentry (optional)
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
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

# Authentication (auto-generated if not set)
JWT_SECRET_KEY=dev-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# OAuth (optional for development)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# CORS (Frontend URLs)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=200

# Logging (development: human-readable)
LOG_LEVEL=INFO
LOG_FORMAT=text

# Sentry (optional - leave empty to disable)
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

**`frontend/.env.local`:**
```bash
# Sentry (optional)
VITE_SENTRY_DSN=
VITE_SENTRY_ENVIRONMENT=development
VITE_APP_VERSION=0.1.0
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

# Authentication
JWT_SECRET_KEY=production-jwt-secret-generate-with-openssl

# OAuth
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Sentry
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/1234567
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
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

# Authentication
JWT_SECRET_KEY=production-jwt-secret-here

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTH_REDIRECT_BASE_URL=https://storai.example.com

# CORS (production domain)
CORS_ORIGINS=["https://storai.example.com"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=60

# Sentry
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/1234567
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
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

### 2. JWT Keys

**Generate Secure JWT Key:**
```bash
openssl rand -hex 32
```

**Best Practices:**
- Use different keys for development and production
- Rotate keys periodically (quarterly)
- Store securely in secrets manager

### 3. API Keys

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

### 4. OAuth Credentials

**Security:**
- Use separate OAuth apps for dev/staging/production
- Restrict redirect URIs to specific domains
- Keep client secrets confidential
- Rotate secrets if compromised

### 5. Database Credentials

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

### 6. Storage Credentials

**MinIO/S3:**
```bash
# Bad (default MinIO)
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin

# Good (production)
S3_ACCESS_KEY_ID=admin-$(openssl rand -hex 8)
S3_SECRET_ACCESS_KEY=$(openssl rand -base64 32)
```

### 7. CORS Configuration

**Development:**
```bash
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

**Production (Strict):**
```bash
CORS_ORIGINS=["https://storai.example.com"]
# Never use "*" in production!
```

### 8. Rate Limiting

**Adjust Based on Traffic:**
```bash
# Development: lenient
RATE_LIMIT_PER_MINUTE=200

# Production: strict
RATE_LIMIT_PER_MINUTE=60

# High-traffic production
RATE_LIMIT_PER_MINUTE=100
```

### 9. Environment File Permissions

```bash
# Restrict access to .env files
chmod 600 backend/.env
chmod 600 .env.production

# Verify
ls -la backend/.env  # Should show: -rw-------
```

### 10. Git Ignore

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

### "OAuth callback failed" errors

**Check:**
- Redirect URI matches exactly (including trailing slashes)
- Client ID and Secret are correct
- OAuth app is not in "Testing" mode (Google)
- Authorized domains are configured

### "JWT token invalid" errors

**Check:**
- JWT_SECRET_KEY is the same across all instances
- Token hasn't expired
- Clock sync between servers

### "Sentry not receiving events" errors

**Check:**
- SENTRY_DSN is correctly formatted
- DSN includes the full URL with project ID
- Network connectivity to Sentry servers
- Sample rate is not set to 0

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

**Last Updated**: 2025-12-20
**Version**: Phase 6
