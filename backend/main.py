"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.core.config import settings
from app.core.database import db
from app.core.logging import configure_logging
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.middleware.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware


# Configure logging before anything else
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.env}")

    # Connect to MongoDB
    await db.connect_db()

    yield

    # Shutdown
    logger.info("Shutting down application")
    await db.close_db()


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered storybook and comic book generation API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter state to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request context middleware (add first to ensure correlation IDs are available)
app.add_middleware(RequestContextMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure response compression (GZip)
# Compresses responses larger than 500 bytes with minimum quality of 5
app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=5)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_request_size=10 * 1024 * 1024)  # 10 MB

# Register error handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Checks the status of the application, database, and storage.
    """
    health_status = {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.env,
        "services": {
            "database": "unknown",
            "storage": "unknown",
        },
    }

    # Check database
    try:
        await db.get_client().admin.command("ping")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check storage
    try:
        from app.services.storage import storage_service
        if storage_service.health_check():
            health_status["services"]["storage"] = "healthy"
        else:
            health_status["services"]["storage"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["storage"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/health",
    }


# Include API routers
from app.api import stories
from app.api import settings as settings_router
from app.api import auth
from app.api import exports
from app.api import templates
from app.api import sharing
from app.api import bookmarks

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(exports.router, prefix="/api/exports", tags=["exports"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(sharing.router, prefix="/api", tags=["sharing"])
app.include_router(bookmarks.router, prefix="/api", tags=["bookmarks"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
