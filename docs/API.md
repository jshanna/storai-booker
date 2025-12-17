# StorAI-Booker API Documentation

Complete REST API reference for the StorAI-Booker backend.

**Base URL**: `http://localhost:8000`
**API Prefix**: `/api`
**Interactive Docs**: http://localhost:8000/api/docs

## Table of Contents

- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Stories API](#stories-api)
- [Settings API](#settings-api)
- [System Endpoints](#system-endpoints)
- [Rate Limiting](#rate-limiting)
- [Correlation IDs](#correlation-ids)

## Authentication

**Current Version**: No authentication required

All endpoints are publicly accessible. User authentication will be added in Phase 6.

## Error Handling

### Error Response Format

All errors follow a structured format with correlation IDs for tracing:

```json
{
  "error": {
    "type": "http_error" | "validation_error" | "internal_error",
    "status_code": 400,
    "message": "Human-readable error message",
    "path": "/api/stories/invalid-id",
    "correlation_id": "3cb6bfc0-e0b3-4786-8642-4f5c86588f3e",
    "details": []  // Optional: validation details
  }
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 202 | Accepted | Async story generation started |
| 400 | Bad Request | Invalid request data or parameters |
| 404 | Not Found | Resource doesn't exist |
| 413 | Payload Too Large | Request body exceeds 10MB |
| 422 | Unprocessable Entity | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Error Types

**http_error**: Standard HTTP errors (404, 400, etc.)
```json
{
  "error": {
    "type": "http_error",
    "status_code": 404,
    "message": "Story 123abc not found"
  }
}
```

**validation_error**: Request validation failures
```json
{
  "error": {
    "type": "validation_error",
    "status_code": 422,
    "message": "Request validation failed",
    "details": [
      {
        "field": "body.generation_inputs.audience_age",
        "message": "ensure this value is greater than or equal to 3",
        "type": "value_error.number.not_ge"
      }
    ]
  }
}
```

**internal_error**: Server errors
```json
{
  "error": {
    "type": "internal_error",
    "status_code": 500,
    "message": "An unexpected error occurred"
  }
}
```

## Stories API

### POST /api/stories/generate

Generate a new story (asynchronous operation).

**Request Body:**
```json
{
  "title": "The Brave Little Dragon",
  "generation_inputs": {
    "audience_age": 7,
    "topic": "A young dragon learning to fly",
    "setting": "Magical mountain kingdom",
    "format": "storybook",
    "illustration_style": "watercolor",
    "characters": [
      "Sparkle the dragon",
      "Luna the wise owl"
    ],
    "page_count": 10
  }
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | 1-200 chars | Story title |
| `generation_inputs.audience_age` | integer | Yes | 3-12 | Target age |
| `generation_inputs.topic` | string | Yes | 1-500 chars | Story theme/plot |
| `generation_inputs.setting` | string | Yes | 1-500 chars | Story location/world |
| `generation_inputs.format` | string | Yes | "storybook" or "comic" | Format type |
| `generation_inputs.illustration_style` | string | Yes | See styles below | Art style |
| `generation_inputs.characters` | string[] | Yes | 1-5 items, max 200 chars each | Main characters |
| `generation_inputs.page_count` | integer | Yes | 5-20 | Number of pages |

**Illustration Styles:**
- `watercolor` - Soft, flowing watercolor paintings
- `digital_art` - Modern digital illustration
- `cartoon` - Playful cartoon style
- `pencil_sketch` - Hand-drawn pencil art
- `oil_painting` - Classic oil painting style
- `anime` - Japanese anime/manga style

**Response (202 Accepted):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "title": "The Brave Little Dragon",
  "created_at": "2025-12-17T12:30:00Z",
  "updated_at": "2025-12-17T12:30:00Z",
  "generation_inputs": { /* ... */ },
  "metadata": {
    "total_pages": 10,
    "format": "storybook",
    "illustration_style": "watercolor"
  },
  "pages": [],
  "status": "pending",
  "error_message": null,
  "cover_image_url": null
}
```

**Story Generation Process:**

1. **pending**: Story created, queued for generation
2. **generating**: Celery worker processing (3-5 minutes)
   - Planning phase
   - Character sheet generation
   - Page-by-page generation
   - Cover creation
3. **complete**: Story ready with all images
4. **error**: Generation failed (check `error_message`)

**Content Validation:**

Stories are validated for:
- Age-appropriate language and themes
- NSFW content (rejected)
- Violence/scary content for young ages
- Input sanitization (XSS, injection prevention)

**Errors:**

- `400 Bad Request`: Invalid input (age outside range, topic inappropriate)
- `500 Internal Server Error`: Generation system error

---

### GET /api/stories

List stories with pagination, filtering, and search.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 10 | Items per page (1-100) |
| `format` | string | null | Filter by format: "storybook" or "comic" |
| `status` | string | null | Filter by status: "pending", "generating", "complete", "error" |
| `search` | string | null | Search in title (full-text search) |

**Example Requests:**
```bash
# Get first page (default 10 items)
GET /api/stories

# Get page 2 with 20 items
GET /api/stories?page=2&page_size=20

# Filter by format
GET /api/stories?format=storybook

# Filter by status
GET /api/stories?status=complete

# Search titles
GET /api/stories?search=dragon

# Combine filters
GET /api/stories?format=storybook&status=complete&search=dragon
```

**Response (200 OK):**
```json
{
  "stories": [
    {
      "id": "676195ef6f8a52ac7cf56896",
      "title": "The Brave Little Dragon",
      "created_at": "2025-12-17T12:30:00Z",
      "updated_at": "2025-12-17T12:35:00Z",
      "generation_inputs": { /* ... */ },
      "metadata": {
        "total_pages": 10,
        "format": "storybook",
        "illustration_style": "watercolor"
      },
      "pages": [ /* full page data */ ],
      "status": "complete",
      "error_message": null,
      "cover_image_url": "https://storage.example.com/covers/123.jpg"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10
}
```

**Caching:**

List responses are cached for 2 minutes. Cache is invalidated when:
- New story is created
- Story is deleted

---

### GET /api/stories/:id

Get a specific story by ID.

**Path Parameters:**
- `id`: MongoDB ObjectId (24-character hex string)

**Example:**
```bash
GET /api/stories/676195ef6f8a52ac7cf56896
```

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "title": "The Brave Little Dragon",
  "created_at": "2025-12-17T12:30:00Z",
  "updated_at": "2025-12-17T12:35:00Z",
  "generation_inputs": {
    "audience_age": 7,
    "topic": "A young dragon learning to fly",
    "setting": "Magical mountain kingdom",
    "format": "storybook",
    "illustration_style": "watercolor",
    "characters": ["Sparkle the dragon", "Luna the wise owl"],
    "page_count": 10
  },
  "metadata": {
    "total_pages": 10,
    "format": "storybook",
    "illustration_style": "watercolor",
    "character_sheets": {
      "Sparkle the dragon": {
        "description": "A small purple dragon with golden eyes...",
        "image_url": "https://storage.example.com/characters/sparkle.jpg"
      }
    },
    "outline": ["Introduction", "Rising Action", ...]
  },
  "pages": [
    {
      "page_number": 1,
      "text": "Once upon a time, in a magical mountain kingdom...",
      "illustration_prompt": "A small purple dragon with golden eyes...",
      "image_url": "https://storage.example.com/pages/page1.jpg",
      "validated": true,
      "validation_notes": null
    }
  ],
  "status": "complete",
  "error_message": null,
  "cover_image_url": "https://storage.example.com/covers/123.jpg"
}
```

**Caching:**

Individual stories are cached for 5 minutes.

**Errors:**
- `400 Bad Request`: Invalid ID format
- `404 Not Found`: Story doesn't exist

---

### GET /api/stories/:id/status

Get story generation status (lightweight endpoint for polling).

**Path Parameters:**
- `id`: Story ID

**Example:**
```bash
GET /api/stories/676195ef6f8a52ac7cf56896/status
```

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "status": "generating",
  "progress": 0.6,
  "current_step": "Generating page 7/10",
  "error_message": null
}
```

**Status Values:**
- `pending`: Queued, not started
- `generating`: In progress (progress: 0.0-1.0)
- `complete`: Finished (progress: 1.0)
- `error`: Failed (check error_message)

**Progress Calculation:**

For generating status:
- Progress = completed_pages / total_pages
- current_step describes current operation

**Use Case:**

Frontend polls this endpoint every 5 seconds during generation for real-time updates.

**Errors:**
- `400 Bad Request`: Invalid ID format
- `404 Not Found`: Story doesn't exist

---

### DELETE /api/stories/:id

Delete a story and its associated files.

**Path Parameters:**
- `id`: Story ID

**Example:**
```bash
DELETE /api/stories/676195ef6f8a52ac7cf56896
```

**Response (204 No Content):**

Empty response body on success.

**Side Effects:**
- Story document deleted from MongoDB
- All associated images deleted from MinIO storage:
  - Character reference sheets
  - Page illustrations
  - Cover image
- Cache entries invalidated

**Errors:**
- `400 Bad Request`: Invalid ID format
- `404 Not Found`: Story doesn't exist
- `500 Internal Server Error`: Deletion failed

---

## Settings API

### GET /api/settings

Get application settings.

**Example:**
```bash
GET /api/settings
```

**Response (200 OK):**
```json
{
  "id": "default",
  "user_id": "default",
  "llm_provider": {
    "google_api_key": "***KEY_SET***",
    "openai_api_key": null,
    "anthropic_api_key": null,
    "default_provider": "google",
    "text_model": "gemini-2.5-flash",
    "image_model": "gemini-2.5-flash-image"
  },
  "generation_defaults": {
    "default_format": "storybook",
    "default_style": "watercolor",
    "default_page_count": 10,
    "retry_limit": 3,
    "max_concurrent_pages": 5
  },
  "content_filters": {
    "nsfw_filter_enabled": true,
    "violence_filter_level": "moderate",
    "scary_content_allowed": false
  },
  "age_range": {
    "min": 3,
    "max": 12,
    "enforce": true
  }
}
```

**API Key Masking:**

API keys are masked in responses for security:
- If set: `"***KEY_SET***"`
- If not set: `null`

---

### PUT /api/settings

Update application settings.

**Request Body:**
```json
{
  "llm_provider": {
    "google_api_key": "AIzaSy...",
    "default_provider": "google",
    "text_model": "gemini-2.5-flash"
  },
  "generation_defaults": {
    "default_format": "storybook",
    "default_style": "watercolor",
    "default_page_count": 10
  },
  "age_range": {
    "min": 5,
    "max": 10,
    "enforce": true
  }
}
```

**Partial Updates:**

You can update only specific sections:
```json
{
  "llm_provider": {
    "google_api_key": "AIzaSy..."
  }
}
```

**API Key Encryption:**

API keys are encrypted at rest using Fernet encryption (AES-128-CBC + HMAC-SHA256).

**Response (200 OK):**

Returns updated settings (with API keys masked).

**Validation:**
- Age range: min >= 3, max <= 12
- Provider: must be "google", "openai", or "anthropic"
- Models: validated against provider
- Retry limit: 1-10
- Max concurrent pages: 1-10

**Errors:**
- `422 Unprocessable Entity`: Validation failed

---

### POST /api/settings/reset

Reset settings to defaults.

**Example:**
```bash
POST /api/settings/reset
```

**Response (200 OK):**

Returns default settings.

**Default Values:**
- Provider: Google Gemini
- Format: Storybook
- Style: Watercolor
- Pages: 10
- Age range: 3-12
- NSFW filter: Enabled

---

## System Endpoints

### GET /health

Health check endpoint.

**Example:**
```bash
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app": "StorAI-Booker",
  "version": "0.1.0",
  "environment": "development",
  "services": {
    "database": "healthy",
    "storage": "healthy"
  }
}
```

**Service Status:**
- `healthy`: Service operational
- `unhealthy`: Service unavailable
- `unknown`: Unable to check

**Status Codes:**
- `200`: All services healthy
- `200` with `status: "degraded"`: Some services unhealthy

---

### GET /

Root endpoint with API information.

**Example:**
```bash
GET /
```

**Response (200 OK):**
```json
{
  "app": "StorAI-Booker",
  "version": "0.1.0",
  "docs": "/api/docs",
  "health": "/health"
}
```

---

## Rate Limiting

**Default Limit**: 100 requests per minute per IP address

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1703088000
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "Rate limit exceeded: 100 per 1 minute"
}
```

**Configuration:**

Set `RATE_LIMIT_PER_MINUTE` in backend/.env to adjust limit.

---

## Correlation IDs

Every request receives a unique correlation ID for tracing.

**Response Header:**
```
X-Correlation-ID: 3cb6bfc0-e0b3-4786-8642-4f5c86588f3e
```

**Error Responses Include Correlation ID:**
```json
{
  "error": {
    "correlation_id": "3cb6bfc0-e0b3-4786-8642-4f5c86588f3e",
    ...
  }
}
```

**Custom Correlation ID:**

Send `X-Correlation-ID` header in request to use custom ID:
```bash
curl -H "X-Correlation-ID: my-custom-id" http://localhost:8000/api/stories
```

**Logging:**

All requests logged with correlation ID for debugging:
```json
{
  "message": "Request completed: GET /api/stories",
  "correlation_id": "3cb6bfc0-e0b3-4786-8642-4f5c86588f3e",
  "status_code": 200,
  "duration_ms": 15.23
}
```

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Generate story
response = requests.post(f"{BASE_URL}/api/stories/generate", json={
    "title": "Dragon Adventure",
    "generation_inputs": {
        "audience_age": 7,
        "topic": "A brave dragon",
        "setting": "Magic forest",
        "format": "storybook",
        "illustration_style": "watercolor",
        "characters": ["Sparkle the dragon"],
        "page_count": 5
    }
})
story = response.json()
story_id = story["id"]

# Poll status
import time
while True:
    status_response = requests.get(f"{BASE_URL}/api/stories/{story_id}/status")
    status = status_response.json()

    if status["status"] == "complete":
        break
    elif status["status"] == "error":
        raise Exception(status["error_message"])

    print(f"Progress: {status['progress']:.0%} - {status['current_step']}")
    time.sleep(5)

# Get complete story
story_response = requests.get(f"{BASE_URL}/api/stories/{story_id}")
final_story = story_response.json()
print(f"Story complete with {len(final_story['pages'])} pages!")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

async function generateStory() {
  // Create story
  const response = await fetch(`${BASE_URL}/api/stories/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: "Dragon Adventure",
      generation_inputs: {
        audience_age: 7,
        topic: "A brave dragon",
        setting: "Magic forest",
        format: "storybook",
        illustration_style: "watercolor",
        characters: ["Sparkle the dragon"],
        page_count: 5
      }
    })
  });

  const story = await response.json();
  const storyId = story.id;

  // Poll status
  while (true) {
    const statusResponse = await fetch(
      `${BASE_URL}/api/stories/${storyId}/status`
    );
    const status = await statusResponse.json();

    if (status.status === "complete") {
      break;
    } else if (status.status === "error") {
      throw new Error(status.error_message);
    }

    console.log(`Progress: ${(status.progress * 100).toFixed(0)}%`);
    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  // Get complete story
  const finalResponse = await fetch(`${BASE_URL}/api/stories/${storyId}`);
  const finalStory = await finalResponse.json();

  return finalStory;
}
```

---

## Versioning

**Current Version**: v1 (implicit)

API versioning will be introduced in Phase 6. Breaking changes will be communicated via:
- Version prefix in URL (`/api/v2/...`)
- Deprecation headers
- Changelog in docs

---

**Last Updated**: 2025-12-17
**Version**: Phase 5
