"""
Cart Service API Routes.
Exposes shopping cart operations for customer and guest footwear shoppers.
"""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_cart_identity, get_current_user_claims
from app.schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartMergeRequest,
    CartResponse,
    CartValidationResponse,
)
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Get current shopping cart for customer or guest session",
)
async def get_current_cart(
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve active footwear items, subtotals, and overall cart price."""
    svc = CartService(db)
    return await svc.get_cart(
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Add a footwear variant to the shopping cart",
)
async def add_cart_item(
    item_in: CartItemAdd,
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """
    Add shoe variant to cart with selected heel customization (1, 2, or 3-inch).
    Validates stock availability with Inventory Service before appending.
    """
    svc = CartService(db)
    return await svc.add_item(
        item_in=item_in,
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )


@router.patch(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Update quantity of a footwear variant in the cart",
)
async def update_cart_item_quantity(
    item_id: uuid.UUID,
    req: CartItemUpdate,
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """Adjust footwear pair count (1-10) with inventory availability re-check."""
    svc = CartService(db)
    return await svc.update_item_quantity(
        item_id=item_id,
        req=req,
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Remove a footwear item from the shopping cart",
)
async def remove_cart_item(
    item_id: uuid.UUID,
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """Delete variant from cart and return recalculated cart totals."""
    svc = CartService(db)
    return await svc.remove_item(
        item_id=item_id,
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )


@router.delete(
    "/clear",
    response_model=CartResponse,
    summary="Clear all footwear items from the shopping cart",
)
async def clear_cart(
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """Empty cart contents."""
    svc = CartService(db)
    return await svc.clear_cart(
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )


@router.post(
    "/merge",
    response_model=CartResponse,
    summary="Merge guest session cart into logged-in customer cart",
)
async def merge_cart(
    req: CartMergeRequest,
    user_claims: Dict[str, Any] = Depends(get_current_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """
    Invoked when customer logs in.
    Transfers all items from guest session cart into customer's persistent user cart.
    """
    svc = CartService(db)
    return await svc.merge_guest_cart(
        user_id=user_claims["user_id"],
        guest_session_id=req.guest_session_id,
    )


@router.post(
    "/validate",
    response_model=CartValidationResponse,
    summary="Validate cart items against live inventory stock",
)
async def validate_cart(
    identity: Dict[str, Any] = Depends(get_cart_identity),
    db: AsyncSession = Depends(get_db),
):
    """
    Pre-checkout boundary check: verifies every item in the cart is currently available
    in the Inventory Service.
    """
    svc = CartService(db)
    return await svc.validate_cart(
        user_id=identity["user_id"],
        session_id=identity["session_id"],
    )
