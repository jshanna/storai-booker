"""Global error handling middleware."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions.

    Returns structured error responses for HTTP exceptions.
    """
    # Get correlation ID from request state if available
    correlation_id = getattr(request.state, "correlation_id", None)

    error_response = {
        "error": {
            "type": "http_error",
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path),
        }
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Returns structured error responses for validation failures.
    """
    # Get correlation ID from request state if available
    correlation_id = getattr(request.state, "correlation_id", None)

    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    # Log with correlation ID if available
    log_context = {"path": request.url.path, "errors": errors}
    if correlation_id:
        log_context["correlation_id"] = correlation_id

    logger.warning(f"Validation error on {request.url.path}", **log_context)

    error_response = {
        "error": {
            "type": "validation_error",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Request validation failed",
            "details": errors,
            "path": str(request.url.path),
        }
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Logs the error and returns a generic error response.
    """
    # Get correlation ID from request state if available
    correlation_id = getattr(request.state, "correlation_id", None)

    # Log with correlation ID if available
    log_context = {"path": request.url.path, "error": str(exc)}
    if correlation_id:
        log_context["correlation_id"] = correlation_id

    logger.error(f"Unexpected error on {request.url.path}: {exc}", **log_context, exc_info=True)

    error_response = {
        "error": {
            "type": "internal_error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
        }
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
