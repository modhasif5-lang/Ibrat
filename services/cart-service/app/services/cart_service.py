"""
Cart Service Business Logic Layer.
Orchestrates cart item additions, quantity updates, inventory availability checks,
guest-to-user merges, and order-boundary calculations.
"""

import logging
import uuid
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import (
    CartItemAdd,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
    CartValidationIssue,
    CartValidationResponse,
)
from app.services.inventory_client import inventory_client

logger = logging.getLogger(__name__)


class CartService:
    """Core domain service for shopping cart operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CartRepository(db)

    # ============================================================
    # Cart Serialization Helper
    # ============================================================

    def _build_cart_response(self, cart: Cart) -> CartResponse:
        """Calculate subtotals and format Cart domain model into response schema."""
        item_responses: List[CartItemResponse] = []
        total_items = 0
        total_price = Decimal("0.00")

        for item in cart.items or []:
            subtotal = Decimal(str(item.unit_price)) * item.quantity
            total_items += item.quantity
            total_price += subtotal
            item_responses.append(
                CartItemResponse(
                    id=item.id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    selected_customization=item.selected_customization,
                    unit_price=item.unit_price,
                    subtotal=round(subtotal, 2),
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            session_id=cart.session_id,
            items=item_responses,
            total_items=total_items,
            total_price=round(total_price, 2),
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )

    # ============================================================
    # Cart Operations
    # ============================================================

    async def get_cart(
        self,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartResponse:
        """Fetch existing cart or create a new empty cart for customer/guest."""
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        return self._build_cart_response(cart)

    async def add_item(
        self,
        item_in: CartItemAdd,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartResponse:
        """Add footwear item to cart after verifying inventory availability."""
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)

        # Check existing quantity if already in cart
        existing_qty = 0
        for it in cart.items:
            if (
                it.variant_id == item_in.variant_id
                and it.selected_customization == item_in.selected_customization
            ):
                existing_qty = it.quantity
                break

        target_qty = min(existing_qty + item_in.quantity, 10)

        # Verify stock with Inventory Service
        is_available, stock = await inventory_client.check_availability(
            item_in.variant_id, target_qty
        )
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({target_qty}) exceeds available stock ({stock}).",
            )

        await self.repo.add_item(cart, item_in)
        # Reload cart to recalculate totals
        refreshed_cart = await self.repo.get_cart_by_id(cart.id)
        return self._build_cart_response(refreshed_cart)

    async def update_item_quantity(
        self,
        item_id: uuid.UUID,
        req: CartItemUpdate,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartResponse:
        """Update quantity of an existing cart item."""
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)

        # Find target item
        target_item: Optional[CartItem] = None
        for it in cart.items:
            if it.id == item_id:
                target_item = it
                break

        if not target_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in current cart.",
            )

        # Verify stock with Inventory Service
        is_available, stock = await inventory_client.check_availability(
            target_item.variant_id, req.quantity
        )
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({req.quantity}) exceeds available stock ({stock}).",
            )

        await self.repo.update_item_quantity(cart.id, item_id, req.quantity)
        refreshed_cart = await self.repo.get_cart_by_id(cart.id)
        return self._build_cart_response(refreshed_cart)

    async def remove_item(
        self,
        item_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartResponse:
        """Remove a product item from the cart."""
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        deleted = await self.repo.remove_item(cart.id, item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in current cart.",
            )

        refreshed_cart = await self.repo.get_cart_by_id(cart.id)
        return self._build_cart_response(refreshed_cart)

    async def clear_cart(
        self,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartResponse:
        """Clear all footwear items from the cart."""
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        await self.repo.clear_cart(cart.id)
        refreshed_cart = await self.repo.get_cart_by_id(cart.id)
        return self._build_cart_response(refreshed_cart)

    async def merge_guest_cart(
        self,
        user_id: uuid.UUID,
        guest_session_id: str,
    ) -> CartResponse:
        """Merge guest cart items into authenticated customer's cart upon login."""
        user_cart = await self.repo.get_or_create_cart(user_id=user_id)
        guest_cart = await self.repo.get_cart_by_session_id(guest_session_id)

        if not guest_cart or not guest_cart.items:
            # Nothing to merge
            return self._build_cart_response(user_cart)

        merged_cart = await self.repo.merge_carts(guest_cart, user_cart)
        return self._build_cart_response(merged_cart)

    async def validate_cart(
        self,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None,
    ) -> CartValidationResponse:
        """
        Validate all cart items against real-time inventory levels.
        Identifies any out-of-stock or quantity-exceeded footwear variants.
        """
        cart = await self.repo.get_or_create_cart(user_id=user_id, session_id=session_id)
        issues: List[CartValidationIssue] = []

        for item in cart.items:
            stock = await inventory_client.get_available_quantity(item.variant_id)
            if stock is not None and stock < item.quantity:
                issues.append(
                    CartValidationIssue(
                        variant_id=item.variant_id,
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=stock,
                        message=(
                            f"Variant only has {stock} pairs available (requested {item.quantity})."
                            if stock > 0
                            else "Variant is currently out of stock."
                        ),
                    )
                )

        return CartValidationResponse(
            is_valid=len(issues) == 0,
            total_items=sum(item.quantity for item in cart.items),
            issues=issues,
        )
