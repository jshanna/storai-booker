"""FastAPI dependencies for authentication and authorization."""
from typing import Optional
from fastapi import Header, HTTPException, status, Depends

from app.models.user import User
from app.services.auth import auth_service


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> User:
    """
    Get the current authenticated user from the Authorization header.

    Raises:
        HTTPException: If no token provided, token is invalid, or user not found
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    # Validate token
    payload = auth_service.validate_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is blacklisted
    if await auth_service.is_token_blacklisted_async(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current user and verify they are active.

    Raises:
        HTTPException: If user account is disabled
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user


async def get_optional_user(
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise.

    Useful for endpoints that work both authenticated and anonymous.
    Does not raise errors if no token or invalid token provided.
    """
    if not authorization:
        return None

    # Parse Bearer token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    # Validate token
    payload = auth_service.validate_access_token(token)
    if not payload:
        return None

    # Check if token is blacklisted
    if await auth_service.is_token_blacklisted_async(token):
        return None

    # Get user
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_id(user_id)

    return user


async def get_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current user and verify they are a superuser.

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return current_user
