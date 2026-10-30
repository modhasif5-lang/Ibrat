"""
Cart Service Repository Layer.
Handles persistent CRUD operations for Carts and CartItems using SQLAlchemy 2.0 async sessions.
"""

import uuid
from typing import List, Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.schemas.cart import CartItemAdd


class CartRepository:
    """Encapsulates database access for shopping carts and items."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_cart_by_id(self, cart_id: uuid.UUID) -> Optional[Cart]:
        """Fetch cart by primary UUID with items loaded."""
        stmt = (
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.id == cart_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_cart_by_user_id(self, user_id: uuid.UUID) -> Optional[Cart]:
        """Fetch cart belonging to an authenticated customer."""
        stmt = (
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_cart_by_session_id(self, session_id: str) -> Optional[Cart]:
        """Fetch cart belonging to a guest browsing session."""
        stmt = (
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.session_id == session_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_cart(
        self,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> Cart:
        """Find existing cart for user/session or create a new one."""
        cart: Optional[Cart] = None

        if user_id is not None:
            cart = await self.get_cart_by_user_id(user_id)
            if cart:
                return cart
            cart = Cart(user_id=user_id, session_id=session_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart, ["items"])
            return cart

        if session_id is not None:
            cart = await self.get_cart_by_session_id(session_id)
            if cart:
                return cart
            cart = Cart(session_id=session_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart, ["items"])
            return cart

        # Default fallback guest cart
        cart = Cart(session_id=str(uuid.uuid4()))
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart, ["items"])
        return cart

    async def add_item(self, cart: Cart, item_in: CartItemAdd) -> CartItem:
        """Add item or increment quantity if matching variant & customization already exist."""
        # Find matching item in existing items
        existing_item: Optional[CartItem] = None
        for item in cart.items:
            if (
                item.variant_id == item_in.variant_id
                and item.selected_customization == item_in.selected_customization
            ):
                existing_item = item
                break

        if existing_item:
            # Increment quantity (capped at max 10)
            existing_item.quantity = min(existing_item.quantity + item_in.quantity, 10)
            existing_item.unit_price = item_in.unit_price
            await self.db.commit()
            await self.db.refresh(existing_item)
            return existing_item

        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            variant_id=item_in.variant_id,
            quantity=item_in.quantity,
            selected_customization=item_in.selected_customization,
            unit_price=item_in.unit_price,
        )
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item

    async def update_item_quantity(
        self,
        cart_id: uuid.UUID,
        item_id: uuid.UUID,
        quantity: int,
    ) -> Optional[CartItem]:
        """Update quantity of an existing cart item."""
        stmt = (
            select(CartItem)
            .where(CartItem.id == item_id, CartItem.cart_id == cart_id)
        )
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None

        item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def remove_item(self, cart_id: uuid.UUID, item_id: uuid.UUID) -> bool:
        """Remove a single item from the cart."""
        stmt = (
            delete(CartItem)
            .where(CartItem.id == item_id, CartItem.cart_id == cart_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return (result.rowcount or 0) > 0

    async def clear_cart(self, cart_id: uuid.UUID) -> int:
        """Remove all items from the cart."""
        stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount or 0

    async def merge_carts(self, guest_cart: Cart, user_cart: Cart) -> Cart:
        """Merge items from a guest cart into the authenticated customer's cart."""
        user_items_map = {
            (item.variant_id, item.selected_customization): item
            for item in user_cart.items
        }

        for guest_item in guest_cart.items:
            key = (guest_item.variant_id, guest_item.selected_customization)
            if key in user_items_map:
                existing = user_items_map[key]
                existing.quantity = min(existing.quantity + guest_item.quantity, 10)
                await self.db.delete(guest_item)
            else:
                guest_item.cart_id = user_cart.id

        await self.db.delete(guest_cart)
        await self.db.commit()
        return await self.get_cart_by_id(user_cart.id)
