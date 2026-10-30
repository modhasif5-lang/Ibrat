"""
User Service Database Repository.
Encapsulates all SQLAlchemy queries for users, tokens, wishlists, preferences, and notifications.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import (
    Notification,
    RefreshToken,
    User,
    UserPreference,
    Wishlist,
    WishlistItem,
)


class UserRepository:
    """Data access repository for User Service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # User Operations
    # ============================================================

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by case-insensitive email."""
        stmt = select(User).where(func.lower(User.email) == func.lower(email))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user by primary key."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "CUSTOMER",
    ) -> User:
        """Create and persist a new user."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip() if full_name else None,
            phone=phone.strip() if phone else None,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()

        # Initialize default wishlist and preferences
        wishlist = Wishlist(user_id=user.id)
        preferences = UserPreference(user_id=user.id)
        self.db.add_all([wishlist, preferences])
        await self.db.flush()

        return user

    async def update_user(self, user: User, **kwargs) -> User:
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await self.db.flush()
        return user

    async def list_users(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """List users with pagination, role filtering, and search."""
        offset = (page - 1) * size
        conditions = []

        if role:
            conditions.append(User.role == role)
        if search:
            pattern = f"%{search.strip()}%"
            conditions.append(
                or_(
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )

        # Count query
        count_stmt = select(func.count(User.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Data query
        query_stmt = select(User)
        if conditions:
            query_stmt = query_stmt.where(*conditions)
        query_stmt = query_stmt.order_by(desc(User.created_at)).offset(offset).limit(size)

        result = await self.db.execute(query_stmt)
        items = list(result.scalars().all())
        return items, total

    # ============================================================
    # Refresh Token Operations
    # ============================================================

    async def create_refresh_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Store a new refresh token."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_valid_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        """Retrieve a non-revoked, unexpired refresh token."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now,
            )
            .options(selectinload(RefreshToken.user))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """Revoke a single refresh token."""
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()
        if token:
            token.is_revoked = True
            await self.db.flush()
            return True
        return False

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all active tokens for a user (e.g. on password reset)."""
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
        result = await self.db.execute(stmt)
        for token in result.scalars().all():
            token.is_revoked = True
        await self.db.flush()

    # ============================================================
    # Wishlist Operations
    # ============================================================

    async def get_or_create_wishlist(self, user_id: uuid.UUID) -> Wishlist:
        """Retrieve or initialize customer's wishlist with eager loaded items."""
        stmt = (
            select(Wishlist)
            .where(Wishlist.user_id == user_id)
            .options(selectinload(Wishlist.items))
        )
        result = await self.db.execute(stmt)
        wishlist = result.scalar_one_or_none()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            self.db.add(wishlist)
            await self.db.flush()
            wishlist.items = []
        return wishlist

    async def add_to_wishlist(self, user_id: uuid.UUID, product_id: uuid.UUID) -> WishlistItem:
        """Add a footwear product to user's wishlist if not already present."""
        wishlist = await self.get_or_create_wishlist(user_id)

        # Check existing item
        check_stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == product_id,
        )
        existing = (await self.db.execute(check_stmt)).scalar_one_or_none()
        if existing:
            return existing

        item = WishlistItem(wishlist_id=wishlist.id, product_id=product_id)
        self.db.add(item)
        await self.db.flush()
        return item

    async def remove_from_wishlist(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        """Remove a footwear product from user's wishlist."""
        wishlist = await self.get_or_create_wishlist(user_id)
        stmt = select(WishlistItem).where(
            WishlistItem.wishlist_id == wishlist.id,
            WishlistItem.product_id == product_id,
        )
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()
        if item:
            await self.db.delete(item)
            await self.db.flush()
            return True
        return False

    # ============================================================
    # Footwear Preferences Operations
    # ============================================================

    async def get_or_create_preferences(self, user_id: uuid.UUID) -> UserPreference:
        """Get or initialize user footwear preferences."""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await self.db.execute(stmt)
        pref = result.scalar_one_or_none()
        if not pref:
            pref = UserPreference(user_id=user_id)
            self.db.add(pref)
            await self.db.flush()
        return pref

    async def update_preferences(self, user_id: uuid.UUID, **kwargs) -> UserPreference:
        """Update sizing and style preferences."""
        pref = await self.get_or_create_preferences(user_id)
        for key, value in kwargs.items():
            if hasattr(pref, key) and value is not None:
                setattr(pref, key, value)
        await self.db.flush()
        return pref

    # ============================================================
    # Notifications Operations
    # ============================================================

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> List[Notification]:
        """Fetch latest user notifications."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_unread_notifications(self, user_id: uuid.UUID) -> int:
        """Count unread notifications for badge display."""
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str = "INFO",
    ) -> Notification:
        """Dispatch a new in-app notification."""
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
        )
        self.db.add(notif)
        await self.db.flush()
        return notif

    async def mark_notification_as_read(
        self,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Mark single notification as read."""
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        notif = result.scalar_one_or_none()
        if notif:
            notif.is_read = True
            await self.db.flush()
            return True
        return False

    async def mark_all_notifications_as_read(self, user_id: uuid.UUID) -> int:
        """Mark all notifications read for a user."""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        count = 0
        for notif in result.scalars().all():
            notif.is_read = True
            count += 1
        await self.db.flush()
        return count
