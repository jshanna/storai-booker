# StorAI-Booker Development Plan

## Executive Summary

This document outlines the development roadmap for StorAI-Booker, a web application for generating AI-powered storybooks and comic books. The project is structured in 5 major phases, from foundation to advanced features, with an estimated timeline of 16-20 weeks for MVP and 24-32 weeks for full feature set.

---

## Technology Stack Recommendations

### Frontend
- **Framework**: React 18+ with TypeScript
- **State Management**: Zustand or Redux Toolkit
- **Routing**: React Router v6
- **UI Components**: shadcn/ui or Material-UI
- **Forms**: React Hook Form + Zod validation
- **Comic Rendering**: Konva.js (Canvas) or React-Konva for panel composition
- **Speech Bubbles**: Custom SVG components or react-comic-speech-bubble
- **HTTP Client**: Axios or React Query
- **Build Tool**: Vite

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (recommended) or Flask
- **API Style**: RESTful (can evolve to GraphQL later)
- **Validation**: Pydantic (built into FastAPI)
- **Authentication**: JWT (for future user accounts) via python-jose
- **ASGI Server**: Uvicorn with Gunicorn for production

### Database & Storage
- **Primary Database**: MongoDB 6.0+
- **ODM**: Beanie (async ODM built on Pydantic) or Motor (async driver)
- **Migrations**: Custom migration scripts or mongomigrate (schema flexibility reduces migration needs)
- **File Storage**: AWS S3 or MinIO (S3-compatible) via boto3
- **Cache/Queue**: Redis for caching and Celery for job queues
- **Image Processing**: Pillow (PIL Fork) + OpenCV (optional)

### LLM & AI Integration
- **Agent Framework**: LangChain (Python) or LangGraph
- **Text Generation**: OpenAI API (GPT-4) or Anthropic Claude API
- **Image Generation**:
  - DALL-E 3 (OpenAI)
  - Stable Diffusion via Replicate or local setup
- **Orchestration**: Custom multi-agent system built on LangChain

### Key Python Packages
- **Web Framework**: fastapi, uvicorn, gunicorn
- **Database**: motor (async MongoDB driver), beanie (async ODM), pymongo
- **Validation**: pydantic, pydantic-settings
- **Job Queue**: celery, flower
- **LLM**: langchain, langchain-openai, langchain-anthropic
- **Image Processing**: pillow, opencv-python (optional), cairosvg
- **Storage**: boto3, python-multipart
- **Testing**: pytest, pytest-asyncio, pytest-cov, pytest-mock, httpx (async testing)
- **Linting/Formatting**: ruff, black, mypy
- **Logging**: structlog or loguru
- **Security**: cryptography, passlib, python-jose, slowapi
- **Utilities**: python-dotenv, redis, httpx

### DevOps & Deployment
- **Containerization**: Docker + Docker Compose
- **Hosting**:
  - Frontend: Vercel or Netlify
  - Backend: Railway, Render, Fly.io, or AWS ECS (with Uvicorn/Gunicorn)
  - Database: MongoDB Atlas, AWS DocumentDB, or self-hosted MongoDB
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (errors) + LogTail (logs)

### Why MongoDB for StorAI-Booker?

MongoDB is an excellent choice for this application due to:

1. **Flexible Schema**: Stories can have varying structures (storybooks vs comics, different panel counts)
2. **Nested Documents**: Naturally represents pages, panels, dialogue, and metadata in a single document
3. **JSON-like Structure**: Aligns perfectly with Pydantic models and API responses
4. **Scalability**: Easy horizontal scaling for growing story library
5. **Rich Queries**: Supports complex filtering and aggregation for library views
6. **Atlas Free Tier**: Free M0 cluster perfect for development and MVP
7. **Native Array Support**: Ideal for storing panels, pages, and character arrays
8. **GridFS**: Can store large files if needed (though S3 is preferred for images)
9. **Async Support**: Motor and Beanie provide excellent async/await compatibility with FastAPI
10. **No Migration Overhead**: Schema changes don't require complex migrations

---

## Development Phases

### Phase 0: Project Setup (Week 1)
**Goal**: Establish development environment and project structure

#### Tasks
1. **Repository & Version Control**
   - Initialize monorepo structure (or separate frontend/backend repos)
   - Setup Git workflows (main, develop, feature branches)
   - Configure pre-commit hooks (pre-commit framework for Python)
   - Create .gitignore (Python, Node, environment files) and .env.example files

2. **Frontend Setup**
   - Initialize React + TypeScript + Vite project
   - Configure ESLint + Prettier
   - Setup shadcn/ui or component library
   - Create base folder structure:
     ```
     src/
       components/
       pages/
       hooks/
       services/
       types/
       utils/
       styles/
     ```
   - Configure routing structure

3. **Backend Setup**
   - Initialize Python project with Poetry or pip + virtual environment
   - Setup FastAPI project structure
   - Configure linting (Ruff or Flake8) + formatting (Black)
   - Configure type checking (mypy)
   - Setup folder structure:
     ```
     app/
       api/
         routes/
         dependencies.py
       services/
         agents/
         llm/
         storage/
       models/          # Beanie ODM models
       schemas/         # Pydantic schemas for API
       core/
         config.py      # Settings and configuration
         database.py    # MongoDB connection & initialization
       utils/
     ```
   - Configure environment variables (.env + pydantic-settings)

4. **Database Setup**
   - Install MongoDB locally (via Docker) or setup MongoDB Atlas free tier
   - Initialize Beanie ODM models with Pydantic
   - Configure MongoDB connection with Motor
   - Create database indexes for common queries
   - Setup Redis locally or managed instance

5. **Docker Configuration**
   - Create Dockerfile for frontend
   - Create Dockerfile for backend (Python 3.11+)
   - Create docker-compose.yml for local development
   - Include MongoDB, Redis, and MinIO containers

6. **Documentation**
   - Create CONTRIBUTING.md
   - Setup README.md with quick start guide
   - Document environment variables
   - Create architecture diagram

**Deliverables**: Runnable dev environment, project scaffolding

---

### Phase 1: Core Backend & Database (Weeks 2-4)
**Goal**: Build foundational backend services and data persistence

#### 1.1 Database Schema Implementation
- **Define Beanie ODM models (Pydantic-based) for core collections**:
  - Storybook document model
  - Page subdocument/embedded model
  - ComicPanel subdocument/embedded model
  - GenerationInputs embedded in Storybook
  - Settings document model
- **Create Pydantic schemas for API request/response validation**
- **Define MongoDB indexes for performance**:
  - Index on storybook creation date
  - Index on storybook format (storybook/comic)
  - Compound index for filtering/sorting
- **Seed database with test data**
- **Write database utility functions and async connection management**

#### 1.2 Core API Endpoints
- **Storybook CRUD**:
  - `POST /api/stories/generate` - Initiate generation
  - `GET /api/stories` - List all stories (pagination, filtering)
  - `GET /api/stories/:id` - Get single story
  - `GET /api/stories/:id/status` - Get generation status
  - `DELETE /api/stories/:id` - Delete story
  - `GET /api/stories/:id/pages/:pageNumber` - Get specific page

- **Settings Management**:
  - `GET /api/settings` - Get all settings
  - `PUT /api/settings` - Update settings
  - `POST /api/settings/validate-api-key` - Test LLM connection

#### 1.3 Request Validation & Error Handling
- Implement Pydantic models for all API inputs/outputs
- Create global exception handlers (FastAPI exception handlers)
- Setup request logging middleware
- Implement rate limiting (slowapi or custom middleware)

#### 1.4 File Storage Service
- Setup S3/MinIO client (boto3)
- Create async upload service for images
- Implement signed URL generation (presigned URLs)
- Create delete/cleanup utilities
- Add image optimization (Pillow)

**Deliverables**: Working backend API, database with migrations, file storage

---

### Phase 2: LLM Agent System (Weeks 5-7)
**Goal**: Build the multi-agent story generation system

#### 2.1 LLM Provider Integration
- **Create provider abstraction layer**:
  - OpenAI client wrapper
  - Anthropic Claude client wrapper
  - Provider interface for easy switching
- **Implement retry logic with exponential backoff**
- **Add response caching (Redis)**
- **Create token usage tracking**

#### 2.2 Coordinating Agent
- **Implement Phase 1: Initial Story Planning**:
  - Character description expansion
  - Character relation mapping
  - Story outline generation
  - Page outline generation
  - Illustration style guide creation
- **Add format-specific logic** (storybook vs comic)
- **Comic book enhancements**:
  - Panel layout planning
  - Dialogue placement planning
  - Sound effect suggestions

#### 2.3 Page Generation Agents
- **Create page agent worker system**:
  - Storybook page generator
  - Comic panel generator (handles multiple panels per page)
- **Implement concurrent execution** (Celery tasks)
- **Add context management** (pass story outline, character info)
- **Create prompt templates** (using Jinja2 or LangChain templates):
  - Storybook narrative prompts
  - Comic dialogue and action prompts
  - Illustration prompt generation

#### 2.4 Assembly & Validation Agent
- **Implement coherence checking**:
  - Character consistency validation
  - Narrative flow validation
  - Age-appropriate content check
- **Error detection and correction**:
  - Identify problematic pages
  - Trigger regeneration (with retry limits)
- **Finalization logic**:
  - Title generation (if needed)
  - Metadata compilation
  - Status updates

#### 2.5 Job Queue System
- **Setup Celery with Redis broker**:
  - Story generation tasks
  - Page generation tasks
  - Validation tasks
  - Image generation tasks
- **Implement task progress tracking** (Celery result backend)
- **Add failure handling and retry logic** (Celery retry decorators)
- **Create queue monitoring** (Flower dashboard for Celery)

**Deliverables**: Complete agent orchestration system, working story generation

---

### Phase 3: Image Generation & Processing (Weeks 8-10)
**Goal**: Integrate image generation and comic book composition

#### 3.1 Image Generation Service
- **Integrate DALL-E or Stable Diffusion**:
  - Create image generation client
  - Implement prompt enhancement
  - Add safety filters
  - Handle generation failures gracefully
- **Batch processing for multiple panels**
- **Image quality validation**
- **Cost tracking and limits**

#### 3.2 Storybook Image Pipeline
- **Process illustration prompts**
- **Download and store generated images**
- **Create thumbnails**
- **Generate cover image**

#### 3.3 Comic Book Composition Engine
- **Panel Layout Engine**:
  - Implement grid layouts (2x2, 3x1, etc.) using Pillow
  - Support custom panel arrangements
  - Add panel borders and gutters
  - Handle splash pages

- **Speech Bubble Renderer**:
  - Generate SVG speech bubbles (cairosvg to rasterize)
  - Implement bubble types (speech, thought, narration, shout)
  - Add automatic tail positioning
  - Support multi-line text wrapping (PIL ImageDraw)

- **Text Overlay System**:
  - Dialogue text rendering (PIL ImageFont + ImageDraw)
  - Sound effect text rendering with custom fonts
  - Font selection and sizing
  - Text positioning within panels

- **Page Compositor**:
  - Combine panels into final page (Pillow composite)
  - Apply borders and effects
  - Export as high-quality PNG/JPEG
  - Generate web-optimized versions (PIL optimize)

#### 3.4 Image Storage & CDN
- **Organize storage structure**:
  - Original generated images
  - Composed comic pages
  - Thumbnails and covers
- **Implement CDN caching strategy**
- **Add image optimization pipeline**

**Deliverables**: Complete image generation and comic composition system

---

### Phase 4: Frontend Development (Weeks 11-15)
**Goal**: Build all user-facing interfaces

#### 4.1 Core UI Components
- **Create reusable components**:
  - Button, Input, Select, Textarea
  - Card, Modal, Toast notifications
  - Loading spinners and skeletons
  - Progress bars
  - Form field wrappers

#### 4.2 Generation View
- **Build generation form**:
  - Audience information inputs
  - Story parameters fields
  - Format selector (storybook vs comic)
  - Illustration style dropdown
  - Character input (dynamic list)
  - Page count and panels per page inputs
- **Implement form validation** (Zod schemas)
- **Add format-specific field toggling**
- **Create draft save/load functionality**
- **Build generation progress modal**:
  - Real-time progress updates (WebSocket or polling)
  - Phase indicators (planning, generation, validation, images)
  - Cancel generation option
  - Error display and retry

#### 4.3 Library View
- **Create library grid/list layout**:
  - Story cards with cover, title, metadata
  - Format badges (storybook/comic)
  - Sorting (date, title, age)
  - Filtering (format, age range)
  - Search functionality
- **Implement pagination or infinite scroll**
- **Add view/delete/regenerate actions**
- **Create empty state for no stories**

#### 4.4 Reader Mode
- **Traditional Storybook Reader**:
  - Full-screen modal
  - Image + text layout
  - Page navigation (prev/next, jump to page)
  - Progress indicator
  - Keyboard shortcuts (arrow keys)

- **Comic Book Reader**:
  - Panel-based rendering
  - Speech bubbles with dialogue
  - Sound effects overlay
  - Responsive panel layouts
  - Panel zoom on click (optional)
  - Page navigation

- **Shared Features**:
  - Exit to library
  - Download/export button
  - Responsive design

#### 4.5 Settings View
- **Story Generation Settings Panel**:
  - Age range sliders
  - Content filter toggles
  - Retry limit input
  - Max concurrent pages

- **LLM Provider Settings Panel**:
  - Provider selection dropdown
  - API key inputs (masked)
  - Model selection
  - Test connection button
  - Fallback provider configuration

- **Application Settings Panel**:
  - Theme toggle (light/dark)
  - Default format selection
  - Default illustration style
  - Default page count
  - Auto-save preferences

- **Settings Persistence**:
  - Save to backend
  - Local storage backup
  - Validation before save

#### 4.6 State Management
- **Setup Zustand stores**:
  - Story store (library, current story)
  - Generation store (progress, current job)
  - Settings store
  - UI store (modals, toasts, theme)
- **Implement optimistic updates**
- **Add error state handling**

#### 4.7 API Integration
- **Create API service layer**:
  - Axios instance with interceptors
  - Error handling
  - Request/response transformations
- **Implement React Query hooks**:
  - useStories (fetch library)
  - useStory (fetch single story)
  - useGenerationStatus (poll status)
  - useSettings
  - Mutations for create/update/delete

#### 4.8 Real-time Updates
- **Implement WebSocket connection** or **polling mechanism**
- **Subscribe to generation progress events**
- **Update UI in real-time**
- **Handle connection errors gracefully**

**Deliverables**: Complete frontend application with all views

---

### Phase 5: Polish & Production Readiness (Weeks 16-18)
**Goal**: Optimize, test, and prepare for deployment

#### 5.1 Testing
- **Backend Tests**:
  - Unit tests with pytest
  - Integration tests for API endpoints (TestClient from FastAPI)
  - Agent system tests (mocked LLM responses with pytest-mock)
  - Database integration tests (pytest-asyncio for async tests)
  - Code coverage with pytest-cov (target >80%)

- **Frontend Tests**:
  - Component tests (React Testing Library)
  - Integration tests (user flows)
  - E2E tests (Playwright or Cypress)
  - Visual regression tests (Chromatic)

- **Load Testing**:
  - API endpoint stress tests
  - Concurrent generation handling
  - Database query optimization

#### 5.2 Performance Optimization
- **Frontend**:
  - Code splitting and lazy loading
  - Image optimization (WebP, lazy loading)
  - Bundle size analysis and reduction
  - Lighthouse audits (aim for 90+ scores)

- **Backend**:
  - Database query optimization (indexes, query analysis)
  - Caching strategy (Redis for frequent queries)
  - Connection pooling
  - Response compression

- **Image Processing**:
  - Parallel processing where possible
  - Queue prioritization
  - Aggressive caching

#### 5.3 Security Hardening
- **API Security**:
  - Rate limiting per IP/user (slowapi)
  - Request size limits (FastAPI middleware)
  - NoSQL injection prevention (Pydantic validation, sanitize user inputs)
  - XSS protection (sanitize inputs with bleach or html-sanitizer)
  - CORS configuration (FastAPI CORSMiddleware)
  - Security headers (FastAPI middleware or secure.py)

- **API Key Management**:
  - Encrypt API keys at rest (cryptography.fernet or passlib)
  - Never expose in responses
  - Validate on each use
  - Rotation support

- **Content Safety**:
  - Implement NSFW filter using moderation API
  - Age-appropriate content validation
  - User input sanitization
  - Generated content review

#### 5.4 Error Handling & Logging
- **Comprehensive error handling**:
  - Try-catch blocks in critical paths
  - Graceful degradation
  - User-friendly error messages
  - Error boundary components (React)

- **Logging**:
  - Structured logging (structlog or loguru)
  - Log levels (debug, info, warn, error)
  - Request/response logging (FastAPI middleware)
  - Performance metrics
  - LLM usage tracking
  - JSON log formatting for production

- **Monitoring**:
  - Setup Sentry for error tracking
  - Create alert rules for critical errors
  - Dashboard for key metrics

#### 5.5 Documentation
- **User Documentation**:
  - Getting started guide
  - Feature tutorials
  - FAQ section
  - Troubleshooting guide

- **Developer Documentation**:
  - API documentation (OpenAPI/Swagger)
  - Architecture overview
  - Setup instructions
  - Contributing guidelines
  - Deployment guide

- **Code Documentation**:
  - Python docstrings (Google or NumPy style) for all functions/classes
  - Type hints throughout codebase
  - README files in major directories
  - Inline comments for non-obvious logic

#### 5.6 Deployment Setup
- **Environment Configuration**:
  - Production environment variables
  - Database migration strategy
  - Secret management (AWS Secrets Manager or similar)

- **CI/CD Pipeline**:
  - Automated testing on PRs
  - Automated deployment on merge to main
  - Rollback procedures
  - Database migration automation

- **Infrastructure**:
  - Setup production database (MongoDB Atlas M10+ or AWS DocumentDB)
  - Configure MongoDB replica set for production reliability
  - Configure Redis instance (for caching + Celery broker)
  - Deploy Celery workers (separate containers/processes)
  - Setup S3 buckets with proper policies
  - CDN configuration (CloudFront or similar)
  - Domain and SSL certificates
  - Flower dashboard for Celery monitoring (optional)

- **Monitoring & Alerts**:
  - Application performance monitoring
  - Database monitoring
  - Error rate alerts
  - Cost monitoring for LLM usage

**Deliverables**: Production-ready application, deployed to hosting

---

## Phase 6: Advanced Features (Weeks 19-24+)
**Goal**: Implement nice-to-have features from the spec

### 6.1 Enhanced Comic Features
- Advanced panel layouts (splash pages, irregular shapes)
- Custom speech bubble styles library
- Enhanced sound effect positioning
- Motion blur and speed lines
- Panel transition animations

### 6.2 Export & Sharing
- PDF generation for storybooks
- Comic book format export (CBZ/CBR)
- Print-ready file generation
- Social media sharing
- Embed codes for websites

### 6.3 User Accounts
- User registration and authentication
- Personal libraries
- Cloud sync
- Multi-device access
- Usage quotas

### 6.4 Collaboration
- Shared storybooks
- Collaborative editing
- Comments and feedback
- Version history

### 6.5 Templates & Themes
- Pre-made story templates
- Genre-specific styles
- Character template library
- Quick-start wizards

### 6.6 Accessibility
- Screen reader support
- Keyboard navigation
- High contrast mode
- Text-to-speech integration
- WCAG 2.1 AA compliance

### 6.7 Internationalization
- Multi-language UI
- Story generation in multiple languages
- RTL support for manga mode
- Cultural customization

**Deliverables**: Enhanced feature set based on priority

---

## Minimum Viable Product (MVP) Scope

For fastest time to market, the MVP should include:

### Must-Have Features
1. ✅ **Generation View** - Basic form with all core inputs
2. ✅ **Traditional Storybook Generation** - Full pipeline working
3. ✅ **Library View** - List, view, delete functionality
4. ✅ **Reader Mode** - Basic storybook reader
5. ✅ **Settings** - LLM provider configuration, basic filters
6. ✅ **Local Storage** - Single-user, no accounts needed

### MVP Exclusions (Post-MVP)
- ❌ Comic book generation (defer to v2)
- ❌ User accounts and authentication
- ❌ Export to PDF
- ❌ Advanced settings and customization
- ❌ Sharing features
- ❌ Templates and themes

### MVP Timeline
- **Phases 0-2**: Weeks 1-7 (Foundation + Core Generation)
- **Phase 3**: Weeks 8-10 (Storybook Images Only)
- **Phase 4**: Weeks 11-15 (Frontend - Storybook Features)
- **Phase 5**: Weeks 16-18 (Polish & Deploy)

**Total MVP: ~18 weeks**

---

## Full Feature Timeline

For complete application with comic books:

- **MVP**: Weeks 1-18
- **Comic Book Features**: Weeks 19-24
  - Phase 3 comic composition
  - Phase 4 comic UI components
  - Testing and optimization
- **Advanced Features**: Weeks 25-32+
  - User accounts
  - Export features
  - Templates
  - Accessibility

**Total Full Version: ~24-32 weeks**

---

## Risk Assessment & Mitigation

### High-Risk Areas

1. **LLM API Costs**
   - **Risk**: Generation costs may be prohibitively high
   - **Mitigation**:
     - Implement aggressive caching
     - Set usage limits per session
     - Use cheaper models where quality isn't critical
     - Provide cost estimates before generation

2. **LLM API Reliability**
   - **Risk**: APIs may have downtime or rate limits
   - **Mitigation**:
     - Implement fallback providers
     - Queue system with retry logic
     - Save partial progress
     - User notifications

3. **Image Generation Time**
   - **Risk**: Generating 10+ images per story may take too long
   - **Mitigation**:
     - Parallel generation where possible
     - Progress indicators for user patience
     - Optional "draft mode" with fewer pages
     - Caching/reusing similar prompts

4. **Comic Book Composition Complexity**
   - **Risk**: Panel composition with text overlay is technically complex
   - **Mitigation**:
     - Start with simple layouts
     - Use proven libraries (Konva, Fabric.js)
     - Iterate based on results
     - Consider third-party services

5. **Content Safety**
   - **Risk**: Generated content may be inappropriate
   - **Mitigation**:
     - Multiple validation layers
     - Moderation API integration
     - User reporting
     - Conservative defaults

### Medium-Risk Areas

1. **Database Performance** - Mitigation: Proper indexing, query optimization
2. **File Storage Costs** - Mitigation: Compression, cleanup jobs, quotas
3. **Browser Compatibility** - Mitigation: Modern browsers only initially
4. **Mobile Experience** - Mitigation: Desktop-first, mobile in v2

---

## Success Criteria

### Technical Metrics
- ✅ Story generation success rate: >95%
- ✅ Average generation time: <5 minutes (storybook), <10 minutes (comic)
- ✅ API uptime: >99%
- ✅ Page load time: <2 seconds
- ✅ Lighthouse score: >90

### Business Metrics
- ✅ User retention: >40% (1 week)
- ✅ Average stories per user: >3
- ✅ Generation completion rate: >80%
- ✅ User satisfaction: >4/5 stars

### Quality Metrics
- ✅ Coherence validation pass rate: >90%
- ✅ Age-appropriate content: 100%
- ✅ Bug reports: <5 per 100 users per month

---

## Resource Requirements

### Team Composition (Ideal)
- 1x Full-stack Engineer (Lead)
- 1x Frontend Engineer (React specialist)
- 1x Backend Engineer (Python + FastAPI + AI/ML experience)
- 1x UI/UX Designer
- 1x QA Engineer (part-time)

### Costs (Monthly Estimates)
- **LLM APIs**: $500-2000 (varies with usage)
- **Image Generation**: $300-1000 (varies with usage)
- **Hosting**: $100-300 (Vercel + Railway/Render)
- **Database**: $0-60 (MongoDB Atlas M0 free tier or M10 shared cluster $10-60/month)
- **Storage**: $50-200 (S3/MinIO)
- **Monitoring**: $0-100 (Sentry free tier initially)

**Total Monthly: ~$950-3660** (usage-dependent)

---

## Next Steps

### Immediate Actions
1. ✅ Review and approve this development plan
2. ⬜ Decide on MVP vs full scope
3. ⬜ Choose specific technologies from recommendations
4. ⬜ Setup development environment (Phase 0)
5. ⬜ Create initial project structure
6. ⬜ Begin Phase 1: Core Backend development

### Decision Points
- **Frontend Framework**: React recommended, confirm choice
- **Backend Framework**: FastAPI vs Flask (FastAPI recommended for async support)
- **Database**: MongoDB Atlas (managed) vs self-hosted MongoDB vs AWS DocumentDB
- **Python Dependency Management**: Poetry vs pip + venv (Poetry recommended)
- **LLM Provider**: OpenAI vs Anthropic vs both?
- **Image Provider**: DALL-E vs Stable Diffusion vs both?
- **Hosting**: Self-hosted vs managed services?
- **Scope**: MVP first or build full features from start?

---

**Document Version**: 1.2
**Created**: 2025-12-14
**Last Updated**: 2025-12-14
**Status**: Draft - Awaiting Approval
**Estimated MVP Timeline**: 18 weeks
**Estimated Full Version Timeline**: 24-32 weeks

## Revision History
- **v1.2** (2025-12-14): Updated database to use MongoDB instead of PostgreSQL
  - Changed from PostgreSQL to MongoDB 6.0+
  - Changed from SQLAlchemy + Alembic to Beanie ODM + Motor
  - Removed need for complex migrations (schemaless design)
  - Updated to use MongoDB Atlas for managed hosting
  - Changed NoSQL injection prevention strategies
  - Updated indexes for MongoDB query optimization
  - Updated cost estimates for MongoDB Atlas pricing
- **v1.1** (2025-12-14): Updated backend to use Python 3.11+ with FastAPI instead of Node.js
  - Changed from Express/Fastify to FastAPI
  - Changed from Prisma/TypeORM to SQLAlchemy + Alembic
  - Changed from Bull to Celery for job queues
  - Updated all Python-specific libraries and tools
  - Updated testing to use pytest
  - Updated linting/formatting to Ruff/Black/mypy
- **v1.0** (2025-12-14): Initial development plan with Node.js backend
