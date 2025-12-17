"""API routes for authentication."""
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from loguru import logger

from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.services.auth import auth_service

router = APIRouter()


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse schema."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        email_verified=user.email_verified,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        google_connected=user.google_id is not None,
        github_connected=user.github_id is not None,
    )


async def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> User:
    """Extract and validate user from Authorization header."""
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
            detail="Invalid authorization header format",
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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user with email and password.

    Returns access and refresh tokens on successful registration.
    """
    # Check if email already exists
    existing_user = await auth_service.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user
    user = await auth_service.create_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )

    # Generate tokens
    tokens = auth_service.create_token_pair(user)

    logger.info(f"User registered: {user.email}")
    return TokenResponse(**tokens)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with email and password.

    Returns access and refresh tokens on successful login.
    """
    user = await auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record login
    user.record_login()
    await user.save()

    # Generate tokens
    tokens = auth_service.create_token_pair(user)

    logger.info(f"User logged in: {user.email}")
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using a refresh token.

    Returns new access and refresh tokens.
    """
    # Validate refresh token
    payload = auth_service.validate_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if refresh token is blacklisted
    jti = payload.get("jti")
    if jti and await auth_service.is_refresh_token_blacklisted_async(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Blacklist old refresh token
    await auth_service.blacklist_token(request.refresh_token)

    # Generate new tokens
    tokens = auth_service.create_token_pair(user)

    logger.debug(f"Token refreshed for user: {user.email}")
    return TokenResponse(**tokens)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    authorization: Optional[str] = Header(None),
    request: Optional[RefreshTokenRequest] = None,
):
    """
    Logout user by blacklisting tokens.

    Optionally accepts refresh_token in body to blacklist it too.
    """
    # Blacklist access token if provided
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            await auth_service.blacklist_token(parts[1])

    # Blacklist refresh token if provided
    if request and request.refresh_token:
        await auth_service.blacklist_token(request.refresh_token)

    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get the currently authenticated user's profile.
    """
    user = await get_current_user_from_token(authorization)
    return user_to_response(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Update the current user's profile.
    """
    user = await get_current_user_from_token(authorization)

    # Update fields if provided
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url

    user.update_timestamp()
    await user.save()

    logger.info(f"Profile updated for user: {user.email}")
    return user_to_response(user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Change the current user's password.
    """
    user = await get_current_user_from_token(authorization)

    # Verify user has a password (not OAuth-only)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth-only accounts",
        )

    # Verify current password
    if not auth_service.verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    user.password_hash = auth_service.hash_password(request.new_password)
    user.update_timestamp()
    await user.save()

    logger.info(f"Password changed for user: {user.email}")
    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request a password reset email.

    Note: In production, this would send an email with the reset link.
    For now, it just generates and stores the token.
    """
    user = await auth_service.get_user_by_email(request.email)

    # Always return success to prevent email enumeration
    if not user:
        logger.debug(f"Password reset requested for non-existent email: {request.email}")
        return MessageResponse(message="If the email exists, a password reset link has been sent")

    if not user.password_hash:
        logger.debug(f"Password reset requested for OAuth-only account: {request.email}")
        return MessageResponse(message="If the email exists, a password reset link has been sent")

    # Generate reset token
    reset_token = auth_service.generate_password_reset_token()
    user.password_reset_token = reset_token
    user.password_reset_expires = auth_service.get_password_reset_expiry()
    await user.save()

    # TODO: Send email with reset link
    # For development, log the token
    logger.info(f"Password reset token generated for {user.email}: {reset_token}")

    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using a reset token.
    """
    from datetime import datetime, timezone

    # Find user with matching reset token
    user = await User.find_one(User.password_reset_token == request.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Check if token has expired
    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Update password and clear reset token
    user.password_hash = auth_service.hash_password(request.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.update_timestamp()
    await user.save()

    logger.info(f"Password reset completed for user: {user.email}")
    return MessageResponse(message="Password reset successfully")
