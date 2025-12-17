"""Request context middleware for correlation IDs and request tracking."""
import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Add correlation ID and request tracking to all requests.

    This middleware:
    - Generates a unique correlation ID for each request
    - Logs request/response details with timing
    - Adds correlation ID to response headers
    - Binds context to logger for structured logging
    """

    async def dispatch(self, request: Request, call_next):
        """Process request with correlation ID and timing."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Bind correlation ID to logger context for this request
        request.state.correlation_id = correlation_id
        request.state.start_time = time.time()

        # Create logger with request context
        request_logger = logger.bind(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        # Log incoming request
        request_logger.info(
            f"Request started: {request.method} {request.url.path}",
            query_params=dict(request.query_params),
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate request duration
            duration_ms = (time.time() - request.state.start_time) * 1000

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            # Log response
            request_logger.info(
                f"Request completed: {request.method} {request.url.path}",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as e:
            # Calculate request duration even on error
            duration_ms = (time.time() - request.state.start_time) * 1000

            # Log error with context
            request_logger.error(
                f"Request failed: {request.method} {request.url.path}",
                error=str(e),
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )

            # Re-raise to let error handlers process it
            raise
