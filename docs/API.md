# StorAI-Booker API Documentation

Complete REST API reference for the StorAI-Booker backend.

**Base URL**: `http://localhost:8000`
**API Prefix**: `/api`
**Interactive Docs**: http://localhost:8000/api/docs

## Table of Contents

- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Stories API](#stories-api)
- [Sharing API](#sharing-api)
- [Bookmarks API](#bookmarks-api)
- [Comments API](#comments-api)
- [Templates API](#templates-api)
- [Exports API](#exports-api)
- [Settings API](#settings-api)
- [System Endpoints](#system-endpoints)
- [Rate Limiting](#rate-limiting)
- [Correlation IDs](#correlation-ids)

## Authentication

StorAI-Booker supports multiple authentication methods:

### Session-Based Authentication

Most endpoints use cookie-based sessions for authentication.

### POST /api/auth/register

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-17T12:30:00Z"
}
```

**Errors:**
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Validation failed (weak password, invalid email)

---

### POST /api/auth/login

Log in with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-12-17T12:30:00Z"
}
```

**Headers:**
Sets `Set-Cookie` header with session token.

**Errors:**
- `401 Unauthorized`: Invalid credentials

---

### POST /api/auth/logout

Log out and invalidate session.

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

---

### GET /api/auth/me

Get current authenticated user.

**Headers:**
Requires session cookie.

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56896",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar_url": "https://storage.example.com/avatars/123.jpg",
  "oauth_providers": ["google"],
  "created_at": "2025-12-17T12:30:00Z"
}
```

**Errors:**
- `401 Unauthorized`: Not logged in

---

### PUT /api/auth/me

Update current user profile.

**Request Body:**
```json
{
  "name": "New Name",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Response (200 OK):**

Returns updated user object.

---

### PUT /api/auth/password

Change password.

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newstrongpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

**Errors:**
- `400 Bad Request`: Current password incorrect
- `422 Unprocessable Entity`: New password too weak

---

### OAuth Authentication

#### GET /api/auth/google/authorize

Initiate Google OAuth flow. Redirects to Google for authentication.

**Query Parameters:**
- `redirect_uri` (optional): Post-auth redirect URL

**Response:**
Redirects to Google OAuth consent screen.

---

#### GET /api/auth/google/callback

Google OAuth callback handler.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF token

**Response:**
Redirects to frontend with session established.

---

#### GET /api/auth/github/authorize

Initiate GitHub OAuth flow.

---

#### GET /api/auth/github/callback

GitHub OAuth callback handler.

---

### POST /api/auth/link/:provider

Link an OAuth provider to existing account.

**Path Parameters:**
- `provider`: `google` or `github`

**Response:**
Redirects to OAuth flow.

---

### DELETE /api/auth/unlink/:provider

Unlink an OAuth provider from account.

**Path Parameters:**
- `provider`: `google` or `github`

**Response (200 OK):**
```json
{
  "message": "Provider unlinked successfully"
}
```

**Errors:**
- `400 Bad Request`: Cannot unlink last authentication method

---

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
    "details": []
  }
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 202 | Accepted | Async story generation started |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Not allowed to access resource |
| 404 | Not Found | Resource doesn't exist |
| 413 | Payload Too Large | Request body exceeds 10MB |
| 422 | Unprocessable Entity | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Error Types

**http_error**: Standard HTTP errors (401, 403, 404, etc.)
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

Generate a new story (asynchronous operation). Requires authentication.

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
- `401 Unauthorized`: Not logged in
- `500 Internal Server Error`: Generation system error

---

### GET /api/stories

List current user's stories with pagination, filtering, and search. Requires authentication.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 10 | Items per page (1-100) |
| `format` | string | null | Filter by format: "storybook" or "comic" |
| `status` | string | null | Filter by status: "pending", "generating", "complete", "error" |
| `search` | string | null | Search in title (full-text search) |
| `is_shared` | boolean | null | Filter by sharing status |

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

# Filter by sharing status
GET /api/stories?is_shared=true

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
      "cover_image_url": "https://storage.example.com/covers/123.jpg",
      "is_shared": true,
      "share_token": "abc123def456"
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

Get a specific story by ID. Requires authentication and ownership.

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
  "cover_image_url": "https://storage.example.com/covers/123.jpg",
  "is_shared": false,
  "share_token": null
}
```

**Caching:**

Individual stories are cached for 5 minutes.

**Errors:**
- `400 Bad Request`: Invalid ID format
- `401 Unauthorized`: Not logged in
- `403 Forbidden`: Not the owner
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
- `401 Unauthorized`: Not logged in
- `404 Not Found`: Story doesn't exist

---

### DELETE /api/stories/:id

Delete a story and its associated files. Requires authentication and ownership.

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
- Associated bookmarks deleted
- Associated comments deleted

**Errors:**
- `400 Bad Request`: Invalid ID format
- `401 Unauthorized`: Not logged in
- `403 Forbidden`: Not the owner
- `404 Not Found`: Story doesn't exist
- `500 Internal Server Error`: Deletion failed

---

## Sharing API

### POST /api/stories/:id/share

Enable public sharing for a story. Requires authentication and ownership.

**Path Parameters:**
- `id`: Story ID

**Response (200 OK):**
```json
{
  "share_token": "abc123def456ghi789",
  "share_url": "https://storai.example.com/shared/abc123def456ghi789",
  "is_shared": true,
  "shared_at": "2025-12-17T12:30:00Z"
}
```

---

### DELETE /api/stories/:id/share

Disable public sharing for a story.

**Path Parameters:**
- `id`: Story ID

**Response (200 OK):**
```json
{
  "is_shared": false,
  "message": "Sharing disabled"
}
```

---

### GET /api/shared

List all publicly shared stories (no authentication required).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 12 | Items per page (1-50) |
| `format` | string | null | Filter by format |

**Response (200 OK):**
```json
{
  "stories": [
    {
      "id": "676195ef6f8a52ac7cf56896",
      "title": "The Brave Little Dragon",
      "cover_image_url": "https://storage.example.com/covers/123.jpg",
      "format": "storybook",
      "page_count": 10,
      "owner_name": "John Doe",
      "share_token": "abc123def456",
      "shared_at": "2025-12-17T12:30:00Z",
      "created_at": "2025-12-17T12:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 12
}
```

---

### GET /api/shared/:token

View a shared story by share token (no authentication required).

**Path Parameters:**
- `token`: Share token

**Response (200 OK):**

Returns full story object (same as GET /api/stories/:id).

**Errors:**
- `404 Not Found`: Invalid token or sharing disabled

---

## Bookmarks API

All bookmark endpoints require authentication.

### GET /api/bookmarks

List current user's bookmarked stories.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 12 | Items per page (1-50) |

**Response (200 OK):**
```json
{
  "bookmarks": [
    {
      "id": "676195ef6f8a52ac7cf56896",
      "story_id": "676195ef6f8a52ac7cf56897",
      "story_title": "The Brave Little Dragon",
      "cover_image_url": "https://storage.example.com/covers/123.jpg",
      "format": "storybook",
      "page_count": 10,
      "owner_name": "Jane Smith",
      "share_token": "abc123def456",
      "created_at": "2025-12-17T12:30:00Z",
      "story_created_at": "2025-12-17T12:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 12
}
```

---

### POST /api/bookmarks/:story_id

Bookmark a shared story.

**Path Parameters:**
- `story_id`: Story ID to bookmark

**Response (200 OK):**
```json
{
  "id": "676195ef6f8a52ac7cf56898",
  "story_id": "676195ef6f8a52ac7cf56897",
  "created_at": "2025-12-17T12:30:00Z"
}
```

**Errors:**
- `400 Bad Request`: Story not shared or already bookmarked
- `404 Not Found`: Story doesn't exist

---

### DELETE /api/bookmarks/:story_id

Remove a bookmark.

**Path Parameters:**
- `story_id`: Story ID to unbookmark

**Response (204 No Content):**

Empty response body on success.

**Errors:**
- `404 Not Found`: Bookmark doesn't exist

---

### GET /api/bookmarks/:story_id/status

Check if a story is bookmarked.

**Path Parameters:**
- `story_id`: Story ID to check

**Response (200 OK):**
```json
{
  "is_bookmarked": true,
  "bookmark_id": "676195ef6f8a52ac7cf56898"
}
```

---

## Comments API

### GET /api/stories/:id/comments

List comments on a story. Story must be shared or owned by user.

**Path Parameters:**
- `id`: Story ID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (1-50) |

**Response (200 OK):**
```json
{
  "comments": [
    {
      "id": "676195ef6f8a52ac7cf56899",
      "story_id": "676195ef6f8a52ac7cf56896",
      "user_id": "676195ef6f8a52ac7cf56800",
      "user_name": "Jane Smith",
      "user_avatar_url": "https://storage.example.com/avatars/456.jpg",
      "content": "Beautiful story! My daughter loved it.",
      "created_at": "2025-12-17T14:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### POST /api/stories/:id/comments

Add a comment to a shared story. Requires authentication.

**Path Parameters:**
- `id`: Story ID

**Request Body:**
```json
{
  "content": "This is a wonderful story!"
}
```

**Response (201 Created):**
```json
{
  "id": "676195ef6f8a52ac7cf56899",
  "story_id": "676195ef6f8a52ac7cf56896",
  "user_id": "676195ef6f8a52ac7cf56800",
  "user_name": "John Doe",
  "content": "This is a wonderful story!",
  "created_at": "2025-12-17T14:30:00Z"
}
```

**Validation:**
- Content: 1-1000 characters
- Content is sanitized for XSS

**Errors:**
- `400 Bad Request`: Story not shared
- `401 Unauthorized`: Not logged in
- `422 Unprocessable Entity`: Comment too long/empty

---

### DELETE /api/comments/:id

Delete a comment. Must be comment author or story owner.

**Path Parameters:**
- `id`: Comment ID

**Response (204 No Content):**

Empty response body on success.

**Errors:**
- `401 Unauthorized`: Not logged in
- `403 Forbidden`: Not comment author or story owner
- `404 Not Found`: Comment doesn't exist

---

## Templates API

### GET /api/templates

List available story templates.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | null | Filter by category: "adventure", "fantasy", "educational", etc. |
| `format` | string | null | Filter by format: "storybook" or "comic" |

**Response (200 OK):**
```json
{
  "templates": [
    {
      "id": "dragon-adventure",
      "name": "Dragon Adventure",
      "description": "A brave young dragon embarks on an epic quest",
      "category": "fantasy",
      "format": "storybook",
      "preview_image_url": "https://storage.example.com/templates/dragon.jpg",
      "defaults": {
        "audience_age": 7,
        "topic": "A brave dragon discovers the meaning of courage",
        "setting": "Magical kingdom with mountains and forests",
        "illustration_style": "watercolor",
        "characters": ["Blaze the dragon", "Whisper the fairy guide"],
        "page_count": 10
      }
    }
  ],
  "categories": ["adventure", "fantasy", "educational", "friendship", "nature"]
}
```

---

### GET /api/templates/:id

Get a specific template.

**Path Parameters:**
- `id`: Template ID

**Response (200 OK):**

Returns full template object.

**Errors:**
- `404 Not Found`: Template doesn't exist

---

## Exports API

All export endpoints require authentication and story ownership.

### GET /api/exports/:id/pdf

Export story as PDF.

**Path Parameters:**
- `id`: Story ID

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="story-title.pdf"`

Returns PDF file download.

**Features:**
- Full-resolution illustrations
- Proper page layout
- Cover page included
- Print-ready format

**Errors:**
- `400 Bad Request`: Story not complete
- `404 Not Found`: Story doesn't exist

---

### GET /api/exports/:id/epub

Export story as EPUB e-book.

**Path Parameters:**
- `id`: Story ID

**Response:**
- Content-Type: `application/epub+zip`
- Content-Disposition: `attachment; filename="story-title.epub"`

Returns EPUB file download.

**Features:**
- Compatible with most e-readers
- Embedded illustrations
- Table of contents
- Metadata (title, author, date)

---

### GET /api/exports/:id/cbz

Export story as CBZ comic book archive.

**Path Parameters:**
- `id`: Story ID

**Response:**
- Content-Type: `application/x-cbz`
- Content-Disposition: `attachment; filename="story-title.cbz"`

Returns CBZ file download.

**Features:**
- Standard comic book format
- Full-resolution images
- Compatible with comic reader apps

---

### GET /api/exports/:id/images

Export all story images as ZIP archive.

**Path Parameters:**
- `id`: Story ID

**Response:**
- Content-Type: `application/zip`
- Content-Disposition: `attachment; filename="story-title-images.zip"`

Returns ZIP file download.

**Contents:**
- `cover.jpg` - Cover image
- `page-01.jpg` through `page-XX.jpg` - Page illustrations
- `characters/` - Character reference sheets

---

## Settings API

### GET /api/settings

Get application settings. Requires authentication.

**Example:**
```bash
GET /api/settings
```

**Response (200 OK):**
```json
{
  "id": "default",
  "user_id": "676195ef6f8a52ac7cf56896",
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

### POST /api/settings/test

Test LLM provider connection.

**Request Body:**
```json
{
  "provider": "google",
  "api_key": "AIzaSy..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Connection successful",
  "model_info": {
    "text_model": "gemini-2.5-flash",
    "image_model": "gemini-2.5-flash-image"
  }
}
```

**Errors:**
- `400 Bad Request`: Invalid API key or connection failed

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
    "storage": "healthy",
    "redis": "healthy",
    "celery": "healthy"
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
session = requests.Session()

# Login
response = session.post(f"{BASE_URL}/api/auth/login", json={
    "email": "user@example.com",
    "password": "password123"
})

# Generate story
response = session.post(f"{BASE_URL}/api/stories/generate", json={
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
    status_response = session.get(f"{BASE_URL}/api/stories/{story_id}/status")
    status = status_response.json()

    if status["status"] == "complete":
        break
    elif status["status"] == "error":
        raise Exception(status["error_message"])

    print(f"Progress: {status['progress']:.0%} - {status['current_step']}")
    time.sleep(5)

# Download PDF export
pdf_response = session.get(f"{BASE_URL}/api/exports/{story_id}/pdf")
with open("story.pdf", "wb") as f:
    f.write(pdf_response.content)
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

async function generateStory() {
  // Login
  await fetch(`${BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      email: "user@example.com",
      password: "password123"
    })
  });

  // Create story
  const response = await fetch(`${BASE_URL}/api/stories/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
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
      `${BASE_URL}/api/stories/${storyId}/status`,
      { credentials: "include" }
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

  // Enable sharing
  const shareResponse = await fetch(
    `${BASE_URL}/api/stories/${storyId}/share`,
    {
      method: "POST",
      credentials: "include"
    }
  );
  const shareData = await shareResponse.json();
  console.log(`Share URL: ${shareData.share_url}`);

  return storyId;
}
```

---

## Versioning

**Current Version**: v1 (implicit)

API versioning is available. Breaking changes are communicated via:
- Version prefix in URL (`/api/v2/...`)
- Deprecation headers
- Changelog in docs

---

**Last Updated**: 2025-12-20
**Version**: Phase 6
