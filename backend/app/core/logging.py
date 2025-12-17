"""Logging configuration with structured logging and rotation."""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def configure_logging():
    """Configure loguru logger with appropriate format and rotation."""
    # Remove default handler
    logger.remove()

    # Configure based on format preference
    if settings.log_format == "json":
        # JSON format with loguru's built-in serialization
        logger.add(
            sys.stdout,
            level=settings.log_level,
            serialize=True,  # Use loguru's built-in JSON serialization
        )
    else:
        # Human-readable format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level> | "
            "{extra}"
        )
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.log_level,
            colorize=True,
        )

    # File handler with rotation (only in production)
    if settings.is_production:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger.add(
            log_dir / "app.log",
            level=settings.log_level,
            rotation="100 MB",  # Rotate when file reaches 100MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
            serialize=True,  # JSON format for log files
        )

        # Separate error log file
        logger.add(
            log_dir / "error.log",
            level="ERROR",
            rotation="50 MB",
            retention="90 days",  # Keep error logs longer
            compression="zip",
            serialize=True,  # JSON format for log files
        )

    logger.info(f"Logging configured: level={settings.log_level}, format={settings.log_format}")


def get_logger_with_context(**context):
    """
    Get a logger bound with context fields.

    Args:
        **context: Key-value pairs to add as context

    Returns:
        Logger with bound context

    Example:
        log = get_logger_with_context(request_id="abc123", user_id="user456")
        log.info("Processing request")
    """
    return logger.bind(**context)
