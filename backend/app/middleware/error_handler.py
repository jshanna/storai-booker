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
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path),
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Returns structured error responses for validation failures.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Request validation failed",
                "details": errors,
                "path": str(request.url.path),
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Logs the error and returns a generic error response.
    """
    logger.error(f"Unexpected error on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred",
                "path": str(request.url.path),
            }
        },
    )
