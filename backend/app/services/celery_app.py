"""Celery application configuration for async task processing."""
from celery import Celery
from loguru import logger

from app.core.config import settings


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.

    Returns:
        Configured Celery app instance
    """
    # Create Celery app
    celery_app = Celery(
        "storai-booker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )

    # Configure Celery
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,

        # Result backend settings
        result_expires=3600,  # 1 hour
        result_extended=True,  # Store additional metadata

        # Task execution settings
        task_track_started=True,  # Track when tasks start
        task_time_limit=4500,  # 75 minutes max per task (comics with critics take longer)
        task_soft_time_limit=3600,  # 60 minutes soft limit

        # Worker settings
        worker_prefetch_multiplier=1,  # One task at a time per worker
        worker_max_tasks_per_child=50,  # Recycle workers to prevent memory leaks

        # Task routing
        task_routes={
            "app.tasks.story_generation.generate_story_task": {
                "queue": "story_generation"
            },
            "app.tasks.story_generation.generate_page_task": {
                "queue": "page_generation"
            },
            "app.tasks.story_generation.validate_story_task": {
                "queue": "validation"
            },
        },

        # Task acknowledgement
        task_acks_late=True,  # Acknowledge after task completion
        task_reject_on_worker_lost=True,  # Requeue if worker dies

        # Retry settings
        task_default_retry_delay=60,  # 1 minute between retries
        task_max_retries=3,

        # Progress tracking
        task_send_sent_event=True,
    )

    # Auto-discover tasks
    celery_app.autodiscover_tasks(["app.tasks"])

    logger.info(
        f"Celery app configured with broker: {settings.celery_broker_url}, "
        f"backend: {settings.celery_result_backend}"
    )

    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()


# Health check task
@celery_app.task(name="health_check")
def health_check() -> dict:
    """
    Simple health check task for monitoring.

    Returns:
        Status dictionary
    """
    return {"status": "healthy", "message": "Celery worker is running"}
