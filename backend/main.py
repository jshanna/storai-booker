"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

from app.core.config import settings
from app.core.database import db
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
