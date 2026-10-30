"""
User Service Business Logic Layer.
Handles registration, authentication, JWT tokens, profile management,
footwear preferences, wishlists, notifications, and administrative actions.
"""

import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.config import get_settings
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    AdminUserListResponse,
    AuthResponse,
    NotificationListResponse,
    NotificationResponse,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserPreferenceResponse,
    UserPreferenceUpdateRequest,
    UserProfileUpdateRequest,
    UserRegisterRequest,
    UserResponse,
    WishlistItemResponse,
    WishlistResponse,
)

settings = get_settings()


class UserService:
    """Core domain service for user management and authentication."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    # ============================================================
    # Authentication & Registration
    # ============================================================

    async def register(self, req: UserRegisterRequest) -> AuthResponse:
        """Register a new customer account."""
        # Check email uniqueness
        existing = await self.repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )

        hashed = hash_password(req.password)
        user = await self.repo.create_user(
            email=req.email,
            hashed_password=hashed,
            full_name=req.full_name,
            phone=req.phone,
            role="CUSTOMER",
        )

        # Issue initial welcome notification
        await self.repo.create_notification(
            user_id=user.id,
            title="Welcome to Ibrat!",
            message="Discover our handcrafted premium ladies footwear collection with bespoke heel customization.",
            type="INFO",
        )

        # Generate tokens
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            email=user.email,
        )
        raw_refresh, token_hash, expires_at = generate_refresh_token()
        await self.repo.create_refresh_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        )
        return AuthResponse(token=token_resp, user=UserResponse.model_validate(user))

    async def login(self, req: UserLoginRequest) -> AuthResponse:
        """Authenticate user credentials and issue tokens."""
        user = await self.repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Please contact support.",
            )

        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            email=user.email,
        )
        raw_refresh, token_hash, expires_at = generate_refresh_token()
        await self.repo.create_refresh_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        token_resp = TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        )
        return AuthResponse(token=token_resp, user=UserResponse.model_validate(user))

    async def refresh_access_token(self, req: RefreshTokenRequest) -> TokenResponse:
        """Rotate and issue a new access token using a valid refresh token."""
        token_hash = hash_token(req.refresh_token)
        stored_token = await self.repo.get_valid_refresh_token(token_hash)

        if not stored_token or not stored_token.user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        # Rotate refresh token (revoke old, generate new)
        await self.repo.revoke_refresh_token(token_hash)

        user = stored_token.user
        new_access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            email=user.email,
        )
        new_raw_refresh, new_token_hash, expires_at = generate_refresh_token()
        await self.repo.create_refresh_token(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=expires_at,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh,
            expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        )

    async def logout(self, refresh_token: str) -> None:
        """Revoke a user's refresh token on logout."""
        token_hash = hash_token(refresh_token)
        await self.repo.revoke_refresh_token(token_hash)

    # ============================================================
    # Profile & Preferences
    # ============================================================

    async def get_profile(self, user_id: uuid.UUID) -> UserResponse:
        """Fetch current user profile."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return UserResponse.model_validate(user)

    async def update_profile(self, user_id: uuid.UUID, req: UserProfileUpdateRequest) -> UserResponse:
        """Update full name, phone, or avatar URL."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        updated = await self.repo.update_user(
            user,
            full_name=req.full_name,
            phone=req.phone,
            avatar_url=req.avatar_url,
        )
        return UserResponse.model_validate(updated)

    async def change_password(self, user_id: uuid.UUID, req: PasswordChangeRequest) -> None:
        """Verify old password, update hash, and invalidate all existing sessions."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if not verify_password(req.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password does not match.",
            )

        new_hashed = hash_password(req.new_password)
        await self.repo.update_user(user, hashed_password=new_hashed)
        # Security: revoke all refresh tokens upon password reset
        await self.repo.revoke_all_user_tokens(user_id)

    async def get_preferences(self, user_id: uuid.UUID) -> UserPreferenceResponse:
        """Get customer sizing and style preferences."""
        pref = await self.repo.get_or_create_preferences(user_id)
        return UserPreferenceResponse.model_validate(pref)

    async def update_preferences(
        self, user_id: uuid.UUID, req: UserPreferenceUpdateRequest
    ) -> UserPreferenceResponse:
        """Update customer sizing and heel preferences."""
        # Validation for heel sizes
        if req.preferred_heel and req.preferred_heel not in ["1 inch", "2 inch", "3 inch"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Heel preference must be one of: '1 inch', '2 inch', '3 inch'.",
            )

        pref = await self.repo.update_preferences(
            user_id,
            preferred_size=req.preferred_size,
            preferred_heel=req.preferred_heel,
            preferred_colors=req.preferred_colors,
            newsletter_subscribed=req.newsletter_subscribed,
        )
        return UserPreferenceResponse.model_validate(pref)

    # ============================================================
    # Wishlist
    # ============================================================

    async def get_wishlist(self, user_id: uuid.UUID) -> WishlistResponse:
        """Fetch customer's saved footwear products."""
        wishlist = await self.repo.get_or_create_wishlist(user_id)
        items = [WishlistItemResponse.model_validate(item) for item in wishlist.items]
        return WishlistResponse(
            id=wishlist.id,
            user_id=wishlist.user_id,
            items=items,
        )

    async def add_to_wishlist(self, user_id: uuid.UUID, product_id: uuid.UUID) -> WishlistItemResponse:
        """Add footwear product to wishlist."""
        item = await self.repo.add_to_wishlist(user_id, product_id)
        return WishlistItemResponse.model_validate(item)

    async def remove_from_wishlist(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        """Remove footwear product from wishlist."""
        return await self.repo.remove_from_wishlist(user_id, product_id)

    # ============================================================
    # Notifications
    # ============================================================

    async def get_notifications(self, user_id: uuid.UUID) -> NotificationListResponse:
        """Retrieve notifications and badge count."""
        items = await self.repo.get_user_notifications(user_id)
        unread = await self.repo.count_unread_notifications(user_id)
        return NotificationListResponse(
            unread_count=unread,
            items=[NotificationResponse.model_validate(i) for i in items],
        )

    async def mark_notification_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> bool:
        """Mark single notification as read."""
        return await self.repo.mark_notification_as_read(notification_id, user_id)

    async def mark_all_notifications_read(self, user_id: uuid.UUID) -> int:
        """Mark all notifications as read."""
        return await self.repo.mark_all_notifications_as_read(user_id)

    # ============================================================
    # Administration
    # ============================================================

    async def admin_list_users(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
    ) -> AdminUserListResponse:
        """Admin: Paginated user directory with search."""
        users, total = await self.repo.list_users(page=page, size=size, search=search, role=role)
        return AdminUserListResponse(
            total=total,
            page=page,
            size=size,
            items=[UserResponse.model_validate(u) for u in users],
        )

    async def admin_update_user_status(self, user_id: uuid.UUID, is_active: bool) -> UserResponse:
        """Admin: Activate or deactivate user account."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        updated = await self.repo.update_user(user, is_active=is_active)
        if not is_active:
            # Revoke all tokens if user deactivated
            await self.repo.revoke_all_user_tokens(user_id)
        return UserResponse.model_validate(updated)

    async def admin_update_user_role(self, user_id: uuid.UUID, role: str) -> UserResponse:
        """Admin: Assign role (CUSTOMER or ADMIN)."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        updated = await self.repo.update_user(user, role=role)
        return UserResponse.model_validate(updated)
