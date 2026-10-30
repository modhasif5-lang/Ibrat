"""
User Service Schemas Package.
"""

from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    UserProfileUpdateRequest,
    PasswordChangeRequest,
    UserPreferenceResponse,
    UserPreferenceUpdateRequest,
    WishlistItemResponse,
    WishlistResponse,
    NotificationResponse,
    NotificationListResponse,
    AdminUserListResponse,
    AdminUserStatusUpdateRequest,
    AdminUserRoleUpdateRequest,
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "UserProfileUpdateRequest",
    "PasswordChangeRequest",
    "UserPreferenceResponse",
    "UserPreferenceUpdateRequest",
    "WishlistItemResponse",
    "WishlistResponse",
    "NotificationResponse",
    "NotificationListResponse",
    "AdminUserListResponse",
    "AdminUserStatusUpdateRequest",
    "AdminUserRoleUpdateRequest",
]
