"""
Pydantic validation schemas for User Service.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# Auth Schemas
# ============================================================

class UserRegisterRequest(BaseModel):
    """Payload for customer registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)


class UserLoginRequest(BaseModel):
    """Payload for user login."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload for token refresh."""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Payload to revoke a refresh token."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token details returned upon authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


# ============================================================
# User Profile Schemas
# ============================================================

class UserResponse(BaseModel):
    """Public/authorized user representation."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime


class AuthResponse(BaseModel):
    """Composite response returned on registration and login."""
    token: TokenResponse
    user: UserResponse


class UserProfileUpdateRequest(BaseModel):
    """Payload for updating user profile fields."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)


class PasswordChangeRequest(BaseModel):
    """Payload for changing account password."""
    old_password: str
    new_password: str = Field(..., min_length=8)


# ============================================================
# Footwear Preferences Schemas
# ============================================================

class UserPreferenceResponse(BaseModel):
    """Customer sizing, heel, and style preferences."""
    model_config = ConfigDict(from_attributes=True)

    preferred_size: Optional[str] = None
    preferred_heel: Optional[str] = None  # "1 inch", "2 inch", "3 inch"
    preferred_colors: Optional[str] = None
    newsletter_subscribed: bool = False


class UserPreferenceUpdateRequest(BaseModel):
    """Payload to update sizing and footwear preferences."""
    preferred_size: Optional[str] = Field(None, max_length=20)
    preferred_heel: Optional[str] = Field(None, max_length=20)
    preferred_colors: Optional[str] = None
    newsletter_subscribed: Optional[bool] = None


# ============================================================
# Wishlist Schemas
# ============================================================

class WishlistItemResponse(BaseModel):
    """Individual item in customer's wishlist."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime


class WishlistResponse(BaseModel):
    """Full wishlist with item list."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    items: List[WishlistItemResponse] = []


# ============================================================
# Notification Schemas
# ============================================================

class NotificationResponse(BaseModel):
    """User in-app notification item."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Notification feed with unread count."""
    unread_count: int
    items: List[NotificationResponse]


# ============================================================
# Admin Schemas
# ============================================================

class AdminUserListResponse(BaseModel):
    """Paginated list of users for administration."""
    total: int
    page: int
    size: int
    items: List[UserResponse]


class AdminUserStatusUpdateRequest(BaseModel):
    """Admin request to change user status."""
    is_active: bool


class AdminUserRoleUpdateRequest(BaseModel):
    """Admin request to change user role."""
    role: str = Field(..., pattern="^(CUSTOMER|ADMIN)$")
