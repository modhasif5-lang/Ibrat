"""
Authentication Routes for User Service.
Exposes /register, /login, /refresh, /logout, /me, and /change-password.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    LogoutRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer account",
)
async def register(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new customer with email and password.
    Automatically provisions default wishlist and sizing preferences.
    """
    svc = UserService(db)
    return await svc.register(req)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user and return tokens",
)
async def login(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate customer or administrator with email and password."""
    svc = UserService(db)
    return await svc.login(req)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and issue new access token",
)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rotate an active refresh token to obtain a fresh JWT access token."""
    svc = UserService(db)
    return await svc.refresh_access_token(req)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token on logout",
)
async def logout(
    req: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """Revoke refresh token, terminating the session."""
    svc = UserService(db)
    await svc.logout(req.refresh_token)
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Retrieve identity of current authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change account password",
)
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password and revoke all existing sessions."""
    svc = UserService(db)
    await svc.change_password(current_user.id, req)
    return {"message": "Password changed successfully. Please log in with your new credentials."}
