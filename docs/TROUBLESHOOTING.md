# StorAI-Booker Troubleshooting Guide

Common issues and solutions for StorAI-Booker.

## Table of Contents

- [Infrastructure Issues](#infrastructure-issues)
- [Backend Issues](#backend-issues)
- [Story Generation Issues](#story-generation-issues)
- [Frontend Issues](#frontend-issues)
- [Image Storage Issues](#image-storage-issues)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)

---

## Infrastructure Issues

### Docker Services Won't Start

**Symptom:** `docker compose up -d` fails or services show as unhealthy

**Solutions:**

1. **Check Docker is running:**
```bash
docker info
```

2. **Check for port conflicts:**
```bash
sudo lsof -i :27017  # MongoDB
sudo lsof -i :6379   # Redis
sudo lsof -i :9000   # MinIO
sudo lsof -i :9001   # MinIO Console
```

3. **View service logs:**
```bash
docker compose logs mongodb
docker compose logs redis
docker compose logs minio
```

4. **Restart services:**
```bash
docker compose down
docker compose up -d
```

5. **Fresh start (WARNING: Deletes data):**
```bash
docker compose down -v
docker compose up -d
```

---

### MongoDB Won't Connect

**Symptom:** `Failed to connect to MongoDB` in backend logs

**Solutions:**

1. **Check MongoDB is running:**
```bash
docker ps | grep mongo
# Should show "healthy" status
```

2. **Test MongoDB connection:**
```bash
docker exec -it storai-mongodb mongosh
# Should connect without errors
```

3. **Check MongoDB logs:**
```bash
docker logs storai-mongodb
```

4. **Verify connection string in `.env`:**
```bash
cat backend/.env | grep MONGODB_URL
# Should be: mongodb://localhost:27017
```

5. **Restart MongoDB:**
```bash
docker compose restart mongodb
```

---

### Redis Connection Failures

**Symptom:** `redis.exceptions.ConnectionError`

**Solutions:**

1. **Check Redis is running:**
```bash
docker ps | grep redis
```

2. **Test Redis:**
```bash
docker exec -it storai-redis redis-cli ping
# Should return: PONG
```

3. **Check Redis logs:**
```bash
docker logs storai-redis
```

4. **Verify Redis URL:**
```bash
cat backend/.env | grep REDIS_URL
# Should be: redis://localhost:6379/0
```

---

### MinIO/S3 Access Denied

**Symptom:** `Access Denied` or `SignatureDoesNotMatch` errors

**Solutions:**

1. **Check MinIO is running:**
```bash
docker ps | grep minio
```

2. **Verify credentials in `.env`:**
```bash
cat backend/.env | grep S3_
# ACCESS_KEY_ID and SECRET_ACCESS_KEY should match MinIO
```

3. **Access MinIO console:**
```bash
open http://localhost:9001
# Login: minioadmin / minioadmin (default)
```

4. **Check bucket exists:**
- In MinIO console → Buckets
- Should see `storai-booker-images`

5. **Recreate bucket:**
```bash
docker compose up createbuckets
```

---

## Backend Issues

### Backend Won't Start

**Symptom:** `poetry run python main.py` fails

**Solutions:**

1. **Check Python version:**
```bash
python --version
# Should be 3.10 or higher
```

2. **Reinstall dependencies:**
```bash
cd backend
poetry install
```

3. **Check for syntax errors:**
```bash
poetry run python -m py_compile main.py
```

4. **View detailed error:**
```bash
poetry run python main.py
# Read full stack trace
```

5. **Check port 8000 is free:**
```bash
lsof -ti :8000
# If occupied, kill process or change PORT in .env
```

---

### "Module not found" Errors

**Symptom:** `ModuleNotFoundError: No module named 'X'`

**Solutions:**

1. **Activate poetry shell:**
```bash
cd backend
poetry shell
```

2. **Install missing package:**
```bash
poetry add package-name
```

3. **Reinstall all dependencies:**
```bash
poetry install --no-cache
```

4. **Check pyproject.toml:**
```bash
cat pyproject.toml | grep package-name
```

---

### API Returns 500 Errors

**Symptom:** Internal server errors on API requests

**Solutions:**

1. **Check backend logs:**
- Look for stack traces in terminal running `main.py`
- Check correlation ID in error response

2. **Check database connection:**
```bash
curl http://localhost:8000/health
# Should show database: "healthy"
```

3. **Test specific endpoint:**
```bash
curl -v http://localhost:8000/api/stories
```

4. **Enable debug logging:**
```bash
# In backend/.env
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

5. **Restart backend:**
```bash
# Ctrl+C in terminal
poetry run python main.py
```

---

### Celery Worker Not Processing Tasks

**Symptom:** Stories stuck in "pending" status

**Solutions:**

1. **Check worker is running:**
```bash
ps aux | grep celery
```

2. **Start Celery worker:**
```bash
cd backend
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info
```

3. **Check worker logs:**
- Look for task acknowledgments
- Check for errors in worker terminal

4. **Verify Redis connection:**
```bash
# Worker logs should show "Connected to redis://..."
```

5. **Check Celery configuration:**
```bash
cat backend/.env | grep CELERY
```

6. **Restart worker:**
```bash
# Ctrl+C in worker terminal
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info
```

---

## Story Generation Issues

### Stories Stuck at "Generating..."

**Symptom:** Story remains in "generating" status indefinitely

**Solutions:**

1. **Check Celery worker logs:**
```bash
# Look for errors, exceptions, or API failures
```

2. **Verify Google API key:**
```bash
cat backend/.env | grep GOOGLE_API_KEY
# Should have valid key (not empty)
```

3. **Test API key:**
```bash
# In Python:
poetry run python
>>> from google import genai
>>> client = genai.Client(api_key="your-key")
>>> client.models.list()
# Should list models without error
```

4. **Check task status in MongoDB:**
```bash
docker exec -it storai-mongodb mongosh
use storai_booker
db.storybooks.find({status: "generating"}).pretty()
```

5. **Check Celery task state:**
```bash
# In worker logs, search for task ID
# Look for failures or retries
```

6. **Restart Celery worker:**
```bash
# Stop worker (Ctrl+C)
# Start worker again
```

---

### "Safety Filter" or "Blocked" Errors

**Symptom:** Story fails with safety filter message

**Cause:** Google Gemini safety filters blocked inappropriate content

**Solutions:**

1. **Review topic and characters:**
- Avoid violent, sexual, or scary themes for young ages
- Ensure character descriptions are appropriate

2. **Adjust age:**
- Higher age (10-12) = more relaxed filters
- Lower age (3-5) = stricter filters

3. **Rephrase topic:**
```bash
# Instead of: "A scary monster in dark forest"
# Try: "A friendly creature in magical forest"
```

4. **Check generation logs:**
```bash
# Worker logs show which prompts were blocked
```

5. **Retry with different inputs:**
- Change wording
- Simplify characters
- Adjust setting description

---

### Image Generation Failures

**Symptom:** Story completes but some pages have no images

**Solutions:**

1. **Check image provider:**
```bash
cat backend/.env | grep DEFAULT_IMAGE_MODEL
# Should be: gemini-2.5-flash-image
```

2. **Verify storage connection:**
```bash
curl http://localhost:8000/health
# Check storage: "healthy"
```

3. **Check MinIO for uploaded images:**
```bash
# Open http://localhost:9001
# Navigate to bucket → storai-booker-images
# Check if images exist
```

4. **Review worker logs for image errors:**
```bash
# Look for "Image generation failed" messages
```

5. **Check retry settings:**
```bash
cat backend/.env | grep IMAGE_MAX_RETRIES
# Should be 3 or higher
```

6. **Test image generation manually:**
```bash
poetry run python
>>> from app.services.image.google_imagen import GoogleImagenProvider
>>> provider = GoogleImagenProvider()
>>> # Test image generation
```

---

### Character Inconsistency Issues

**Symptom:** Characters look different across pages

**Cause:** Reference sheet generation or usage failure

**Solutions:**

1. **Check character sheet generation:**
- View story artifacts in frontend
- Verify character reference images exist

2. **Review worker logs:**
```bash
# Search for "character sheet" in logs
# Check for failures
```

3. **Verify reference sheets in storage:**
```bash
# MinIO console → character-sheets folder
```

4. **Regenerate story:**
- Delete problematic story
- Create new one with same inputs

---

## Frontend Issues

### Frontend Won't Start

**Symptom:** `npm run dev` fails

**Solutions:**

1. **Check Node.js version:**
```bash
node --version
# Should be 18 or higher
```

2. **Reinstall dependencies:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

3. **Check for port conflicts:**
```bash
lsof -i :5173  # Vite default port
```

4. **View build errors:**
```bash
npm run dev
# Read full error output
```

5. **Clear Vite cache:**
```bash
rm -rf frontend/.vite
npm run dev
```

---

### API Calls Fail (CORS Errors)

**Symptom:** Console shows CORS errors

**Solutions:**

1. **Check backend CORS settings:**
```bash
cat backend/.env | grep CORS_ORIGINS
# Should include: http://localhost:5173
```

2. **Verify frontend URL:**
```bash
# Frontend should be running on http://localhost:5173
```

3. **Check Vite proxy:**
```bash
cat frontend/vite.config.ts
# Should have proxy: { '/api': {...} }
```

4. **Restart both frontend and backend:**
```bash
# Stop both services
# Start backend first, then frontend
```

---

### Images Not Loading

**Symptom:** Image placeholders or broken images in UI

**Solutions:**

1. **Check image URLs in browser DevTools:**
- Network tab → Look for failed image requests
- Check URLs and status codes

2. **Verify S3_PUBLIC_URL:**
```bash
cat backend/.env | grep S3_PUBLIC_URL
# Should be accessible from browser
```

3. **Test image URL directly:**
```bash
# Copy image URL from story response
curl -I <image-url>
# Should return 200 OK
```

4. **Check MinIO CORS:**
```bash
# MinIO console → Buckets → storai-booker-images → Settings
# Add CORS policy if needed
```

5. **Verify images exist in storage:**
```bash
# MinIO console → Browse bucket
# Check for image files
```

---

### Generation Progress Not Updating

**Symptom:** Progress bar stuck at 0%

**Solutions:**

1. **Check polling interval:**
- Frontend should poll every 5 seconds
- Check browser console for API calls

2. **Verify status endpoint:**
```bash
curl http://localhost:8000/api/stories/{id}/status
```

3. **Check browser console for errors:**
- F12 → Console tab
- Look for failed API requests

4. **Restart frontend:**
```bash
npm run dev
```

---

## Image Storage Issues

### Upload to MinIO Fails

**Symptom:** `S3 upload error` in logs

**Solutions:**

1. **Check MinIO is running:**
```bash
docker ps | grep minio
```

2. **Verify credentials:**
```bash
cat backend/.env | grep S3_
# ACCESS_KEY and SECRET_KEY should match MinIO
```

3. **Test MinIO connection:**
```bash
poetry run python
>>> from app.services.storage import storage_service
>>> storage_service.health_check()
# Should return True
```

4. **Check bucket exists:**
```bash
# MinIO console → Buckets
# Should see storai-booker-images
```

5. **Recreate bucket:**
```bash
docker compose up createbuckets
```

---

### Signed URLs Expire Too Fast

**Symptom:** Images load initially but fail after some time

**Cause:** Default presigned URL expiration (24 hours)

**Solutions:**

1. **Increase expiration time:**
```python
# In backend/app/services/storage.py
# Change expiry parameter in generate_presigned_url()
```

2. **Use public bucket:**
```bash
# MinIO console → Bucket → Access Policy
# Set to "Public" (not recommended for production)
```

3. **Implement URL refresh:**
- Frontend can request new URLs periodically
- Backend endpoint to refresh URLs

---

## Performance Issues

### Slow Story Generation

**Symptom:** Generation takes longer than expected (>10 min for 10 pages)

**Solutions:**

1. **Check concurrent page limit:**
```bash
cat backend/.env | grep MAX_CONCURRENT_PAGES
# Increase to 5-8 for faster generation
```

2. **Monitor worker resource usage:**
```bash
docker stats
# Check CPU and memory for celery-worker
```

3. **Check network latency:**
```bash
# Test API response time
time curl https://generativelanguage.googleapis.com/v1beta/models
```

4. **Reduce page count:**
- Fewer pages = faster generation
- Test with 5 pages first

5. **Check for retries:**
- Worker logs show retry attempts
- Excessive retries slow generation

---

### High Memory Usage

**Symptom:** Docker containers using excessive RAM

**Solutions:**

1. **Check container stats:**
```bash
docker stats
```

2. **Reduce Celery concurrency:**
```bash
# Edit docker-compose.yml
# Change: --concurrency=4 to --concurrency=2
```

3. **Reduce MAX_CONCURRENT_PAGES:**
```bash
# In backend/.env
DEFAULT_MAX_CONCURRENT_PAGES=3
```

4. **Restart containers:**
```bash
docker compose restart celery-worker
```

5. **Limit Docker memory:**
```yaml
# In docker-compose.yml
services:
  celery-worker:
    deploy:
      resources:
        limits:
          memory: 2G  # Limit to 2GB
```

---

### Slow API Responses

**Symptom:** API requests take several seconds

**Solutions:**

1. **Check cache is working:**
```bash
# Redis should cache responses
docker exec -it storai-redis redis-cli
> KEYS stories:*
# Should show cached keys
```

2. **Enable caching:**
```bash
# Ensure Redis is running
docker ps | grep redis
```

3. **Monitor database queries:**
```bash
docker exec -it storai-mongodb mongosh
use storai_booker
db.setProfilingLevel(2)
db.system.profile.find().sort({ts:-1}).limit(5)
```

4. **Add database indexes:**
```bash
# MongoDB indexes on commonly queried fields
db.storybooks.createIndex({status: 1})
db.storybooks.createIndex({created_at: -1})
```

---

## Error Messages

### "Invalid story ID format"

**Cause:** ID is not a valid MongoDB ObjectId

**Solution:**
- IDs must be 24-character hex strings
- Example valid ID: `676195ef6f8a52ac7cf56896`
- Check API call uses correct ID

---

### "Audience age X is outside allowed range"

**Cause:** Age not within configured range (default: 3-12)

**Solutions:**

1. **Adjust age in request:**
```json
{
  "generation_inputs": {
    "audience_age": 7  // Must be 3-12
  }
}
```

2. **Change age range in settings:**
```bash
# Via API or settings UI
# Set age_range.min and age_range.max
```

---

### "Topic contains potentially malicious patterns"

**Cause:** Input sanitizer detected SQL/NoSQL injection attempt

**Solution:**
- Remove special characters from input
- Avoid SQL keywords (SELECT, DROP, etc.)
- Use plain language descriptions

---

### "Rate limit exceeded"

**Cause:** More than 100 requests per minute from same IP

**Solutions:**

1. **Wait 60 seconds and retry**

2. **Increase rate limit:**
```bash
# In backend/.env
RATE_LIMIT_PER_MINUTE=200
```

3. **Use custom correlation ID:**
```bash
# Include in request header
X-Correlation-ID: my-unique-id
```

---

### "Request body too large"

**Cause:** Request exceeds 10MB limit

**Solution:**
- Reduce request size
- Check for large base64-encoded data
- Max limits intentional for DoS protection

---

## Getting Help

If issues persist:

1. **Check logs with correlation ID:**
```bash
# Backend logs
grep "correlation_id:abc123" backend.log

# Worker logs
grep "abc123" celery.log
```

2. **Collect diagnostic info:**
```bash
# System info
docker --version
docker compose version
python --version
node --version

# Service status
docker ps
docker compose ps

# Health check
curl http://localhost:8000/health | jq
```

3. **Create GitHub issue:**
- Include error messages
- Include correlation IDs
- Include steps to reproduce
- Include diagnostic info

---

**Last Updated**: 2025-12-17
**Version**: Phase 5
