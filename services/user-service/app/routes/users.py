"""
User and Profile Routes for User Service.
Exposes /profile, /preferences, /wishlist, /notifications, and /admin endpoints.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import (
    AdminUserListResponse,
    AdminUserRoleUpdateRequest,
    AdminUserStatusUpdateRequest,
    NotificationListResponse,
    UserPreferenceResponse,
    UserPreferenceUpdateRequest,
    UserProfileUpdateRequest,
    UserResponse,
    WishlistItemResponse,
    WishlistResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ============================================================
# Customer Profile & Preferences
# ============================================================

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user's profile details",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch complete profile of the authenticated user."""
    svc = UserService(db)
    return await svc.get_profile(current_user.id)


@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update customer profile details",
)
async def update_profile(
    req: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update full name, phone number, or profile picture."""
    svc = UserService(db)
    return await svc.update_profile(current_user.id, req)


@router.get(
    "/preferences",
    response_model=UserPreferenceResponse,
    summary="Get customer footwear sizing & heel preferences",
)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve saved footwear preferences (preferred shoe size, heel height, colors)."""
    svc = UserService(db)
    return await svc.get_preferences(current_user.id)


@router.put(
    "/preferences",
    response_model=UserPreferenceResponse,
    summary="Update customer footwear preferences",
)
async def update_preferences(
    req: UserPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update footwear sizing and preferred heel customization (1 inch, 2 inch, 3 inch)."""
    svc = UserService(db)
    return await svc.update_preferences(current_user.id, req)


# ============================================================
# Wishlist
# ============================================================

@router.get(
    "/wishlist",
    response_model=WishlistResponse,
    summary="Get customer's saved footwear items",
)
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all footwear product IDs in customer's wishlist."""
    svc = UserService(db)
    return await svc.get_wishlist(current_user.id)


@router.post(
    "/wishlist/{product_id}",
    response_model=WishlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a footwear product to wishlist",
)
async def add_to_wishlist(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a footwear product to customer's wishlist."""
    svc = UserService(db)
    return await svc.add_to_wishlist(current_user.id, product_id)


@router.delete(
    "/wishlist/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a footwear product from wishlist",
)
async def remove_from_wishlist(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a footwear product from customer's wishlist."""
    svc = UserService(db)
    removed = await svc.remove_from_wishlist(current_user.id, product_id)
    return {"success": removed, "message": "Product removed from wishlist."}


# ============================================================
# Notifications
# ============================================================

@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    summary="Get customer notifications feed",
)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch user's in-app notification list and badge unread count."""
    svc = UserService(db)
    return await svc.get_notifications(current_user.id)


@router.patch(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_200_OK,
    summary="Mark single notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a specific notification as read."""
    svc = UserService(db)
    updated = await svc.mark_notification_read(current_user.id, notification_id)
    return {"success": updated}


@router.post(
    "/notifications/read-all",
    status_code=status.HTTP_200_OK,
    summary="Mark all customer notifications as read",
)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for current user."""
    svc = UserService(db)
    count = await svc.mark_all_notifications_read(current_user.id)
    return {"success": True, "count": count}


# ============================================================
# Administrative Endpoints (Admin Role Required)
# ============================================================

@router.get(
    "/admin/list",
    response_model=AdminUserListResponse,
    summary="Admin: Paginated list of users with search and filtering",
)
async def admin_list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, pattern="^(CUSTOMER|ADMIN)$"),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List registered users with administrative controls."""
    svc = UserService(db)
    return await svc.admin_list_users(page=page, size=size, search=search, role=role)


@router.patch(
    "/admin/{user_id}/status",
    response_model=UserResponse,
    summary="Admin: Activate or deactivate a user account",
)
async def admin_update_user_status(
    user_id: uuid.UUID,
    req: AdminUserStatusUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate or reactivate a customer account."""
    svc = UserService(db)
    return await svc.admin_update_user_status(user_id, req.is_active)


@router.patch(
    "/admin/{user_id}/role",
    response_model=UserResponse,
    summary="Admin: Promote or change a user's role",
)
async def admin_update_user_role(
    user_id: uuid.UUID,
    req: AdminUserRoleUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Change a user's role between CUSTOMER and ADMIN."""
    svc = UserService(db)
    return await svc.admin_update_user_role(user_id, req.role)
