"""Security middleware for FastAPI application."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from loguru import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit the size of incoming requests to prevent DoS attacks."""

    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10 MB default
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            max_request_size: Maximum request body size in bytes
        """
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """Check request size before processing."""
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_request_size:
                logger.warning(
                    f"Request size {content_length} exceeds limit {self.max_request_size}"
                )
                raise HTTPException(
                    status_code=413,
                    detail=f"Request body too large. Maximum size is {self.max_request_size / 1024 / 1024:.1f} MB",
                )

        return await call_next(request)
