"""API routes for authentication."""
from fastapi import APIRouter, HTTPException, status, Header, Request
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
    OAuthUrlResponse,
    OAuthCallbackRequest,
    OAuthProvidersResponse,
)
from app.services.auth import auth_service
from app.services.oauth import oauth_service
from app.core.config import settings

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


# OAuth Endpoints

@router.get("/oauth/providers", response_model=OAuthProvidersResponse)
async def get_oauth_providers():
    """
    Get available OAuth providers.

    Returns which OAuth providers are configured and available for use.
    """
    return OAuthProvidersResponse(
        google=oauth_service.is_google_configured(),
        github=oauth_service.is_github_configured(),
    )


@router.get("/oauth/google", response_model=OAuthUrlResponse)
async def get_google_auth_url(request: Request):
    """
    Get Google OAuth authorization URL.

    Initiates the Google OAuth flow by returning the authorization URL.
    The frontend should redirect the user to this URL.
    """
    if not oauth_service.is_google_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    # Build redirect URI for the callback
    redirect_uri = f"{settings.oauth_redirect_url}?provider=google"

    try:
        auth_url, state = oauth_service.get_google_auth_url(redirect_uri)
        return OAuthUrlResponse(authorization_url=auth_url, state=state)
    except Exception as e:
        logger.error(f"Failed to generate Google auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google OAuth",
        )


@router.post("/oauth/google/callback", response_model=TokenResponse)
async def google_oauth_callback(request: OAuthCallbackRequest):
    """
    Handle Google OAuth callback.

    Exchanges the authorization code for user info, creates or updates
    the user account, and returns authentication tokens.
    """
    if not oauth_service.is_google_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    # Validate state parameter
    if not oauth_service.validate_state(request.state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    redirect_uri = f"{settings.oauth_redirect_url}?provider=google"

    try:
        # Exchange code for user info
        user_info = await oauth_service.exchange_google_code(request.code, redirect_uri)

        # Find or create user
        user = await User.find_one(User.google_id == user_info.provider_id)

        if not user:
            # Check if email exists (link accounts)
            user = await auth_service.get_user_by_email(user_info.email)

            if user:
                # Link Google account to existing user
                user.google_id = user_info.provider_id
                if not user.avatar_url and user_info.avatar_url:
                    user.avatar_url = user_info.avatar_url
                if user_info.email_verified:
                    user.email_verified = True
            else:
                # Create new user
                user = await auth_service.create_user(
                    email=user_info.email,
                    google_id=user_info.provider_id,
                    full_name=user_info.full_name,
                    avatar_url=user_info.avatar_url,
                    email_verified=user_info.email_verified,
                )

        # Record login
        user.record_login()
        await user.save()

        # Generate tokens
        tokens = auth_service.create_token_pair(user)

        logger.info(f"User logged in via Google: {user.email}")
        return TokenResponse(**tokens)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete Google OAuth: {str(e)}",
        )


@router.get("/oauth/github", response_model=OAuthUrlResponse)
async def get_github_auth_url(request: Request):
    """
    Get GitHub OAuth authorization URL.

    Initiates the GitHub OAuth flow by returning the authorization URL.
    The frontend should redirect the user to this URL.
    """
    if not oauth_service.is_github_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured",
        )

    # Build redirect URI for the callback
    redirect_uri = f"{settings.oauth_redirect_url}?provider=github"

    try:
        auth_url, state = oauth_service.get_github_auth_url(redirect_uri)
        return OAuthUrlResponse(authorization_url=auth_url, state=state)
    except Exception as e:
        logger.error(f"Failed to generate GitHub auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate GitHub OAuth",
        )


@router.post("/oauth/github/callback", response_model=TokenResponse)
async def github_oauth_callback(request: OAuthCallbackRequest):
    """
    Handle GitHub OAuth callback.

    Exchanges the authorization code for user info, creates or updates
    the user account, and returns authentication tokens.
    """
    if not oauth_service.is_github_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured",
        )

    # Validate state parameter
    if not oauth_service.validate_state(request.state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    redirect_uri = f"{settings.oauth_redirect_url}?provider=github"

    try:
        # Exchange code for user info
        user_info = await oauth_service.exchange_github_code(request.code, redirect_uri)

        # Find or create user
        user = await User.find_one(User.github_id == user_info.provider_id)

        if not user:
            # Check if email exists (link accounts)
            user = await auth_service.get_user_by_email(user_info.email)

            if user:
                # Link GitHub account to existing user
                user.github_id = user_info.provider_id
                if not user.avatar_url and user_info.avatar_url:
                    user.avatar_url = user_info.avatar_url
                if user_info.email_verified:
                    user.email_verified = True
            else:
                # Create new user
                user = await auth_service.create_user(
                    email=user_info.email,
                    github_id=user_info.provider_id,
                    full_name=user_info.full_name,
                    avatar_url=user_info.avatar_url,
                    email_verified=user_info.email_verified,
                )

        # Record login
        user.record_login()
        await user.save()

        # Generate tokens
        tokens = auth_service.create_token_pair(user)

        logger.info(f"User logged in via GitHub: {user.email}")
        return TokenResponse(**tokens)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete GitHub OAuth: {str(e)}",
        )


@router.post("/oauth/google/link", response_model=UserResponse)
async def link_google_account(
    request: OAuthCallbackRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Link Google account to existing user.

    Requires authentication. Links the Google account to the current user.
    """
    user = await get_current_user_from_token(authorization)

    if not oauth_service.is_google_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured",
        )

    if user.google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account already linked",
        )

    # Validate state
    if not oauth_service.validate_state(request.state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    redirect_uri = f"{settings.oauth_redirect_url}?provider=google"

    try:
        user_info = await oauth_service.exchange_google_code(request.code, redirect_uri)

        # Check if this Google account is already linked to another user
        existing_user = await User.find_one(User.google_id == user_info.provider_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Google account is already linked to another user",
            )

        # Link the account
        user.google_id = user_info.provider_id
        if not user.avatar_url and user_info.avatar_url:
            user.avatar_url = user_info.avatar_url
        user.update_timestamp()
        await user.save()

        logger.info(f"Google account linked for user: {user.email}")
        return user_to_response(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to link Google account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link Google account: {str(e)}",
        )


@router.post("/oauth/github/link", response_model=UserResponse)
async def link_github_account(
    request: OAuthCallbackRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Link GitHub account to existing user.

    Requires authentication. Links the GitHub account to the current user.
    """
    user = await get_current_user_from_token(authorization)

    if not oauth_service.is_github_configured():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured",
        )

    if user.github_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub account already linked",
        )

    # Validate state
    if not oauth_service.validate_state(request.state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    redirect_uri = f"{settings.oauth_redirect_url}?provider=github"

    try:
        user_info = await oauth_service.exchange_github_code(request.code, redirect_uri)

        # Check if this GitHub account is already linked to another user
        existing_user = await User.find_one(User.github_id == user_info.provider_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This GitHub account is already linked to another user",
            )

        # Link the account
        user.github_id = user_info.provider_id
        if not user.avatar_url and user_info.avatar_url:
            user.avatar_url = user_info.avatar_url
        user.update_timestamp()
        await user.save()

        logger.info(f"GitHub account linked for user: {user.email}")
        return user_to_response(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to link GitHub account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link GitHub account: {str(e)}",
        )


@router.delete("/oauth/google/unlink", response_model=UserResponse)
async def unlink_google_account(authorization: Optional[str] = Header(None)):
    """
    Unlink Google account from user.

    Requires authentication. Can only unlink if user has another auth method.
    """
    user = await get_current_user_from_token(authorization)

    if not user.google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google account linked",
        )

    # Ensure user has another way to log in
    if not user.password_hash and not user.github_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink: no other authentication method available",
        )

    user.google_id = None
    user.update_timestamp()
    await user.save()

    logger.info(f"Google account unlinked for user: {user.email}")
    return user_to_response(user)


@router.delete("/oauth/github/unlink", response_model=UserResponse)
async def unlink_github_account(authorization: Optional[str] = Header(None)):
    """
    Unlink GitHub account from user.

    Requires authentication. Can only unlink if user has another auth method.
    """
    user = await get_current_user_from_token(authorization)

    if not user.github_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub account linked",
        )

    # Ensure user has another way to log in
    if not user.password_hash and not user.google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink: no other authentication method available",
        )

    user.github_id = None
    user.update_timestamp()
    await user.save()

    logger.info(f"GitHub account unlinked for user: {user.email}")
    return user_to_response(user)
