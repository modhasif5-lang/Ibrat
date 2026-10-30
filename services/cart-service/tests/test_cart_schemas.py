"""
Unit tests for Cart Service Pydantic schemas.
Validates footwear heel customization constraints, item quantities, and pricing calculations.
"""

import uuid
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.schemas.cart import (
    ALLOWED_HEEL_SIZES,
    CartItemAdd,
    CartItemResponse,
    CartItemUpdate,
    CartMergeRequest,
    CartResponse,
    CartValidationResponse,
)


def test_valid_heel_customization():
    """Verify footwear heel customization strictly permits 1, 2, and 3-inch options."""
    for heel in ALLOWED_HEEL_SIZES:
        item = CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=1,
            selected_customization=heel,
            unit_price=Decimal("295.00"),
        )
        assert item.selected_customization == f"HEEL_SIZE: {heel}"

    # Also permits pre-formatted prefix
    item_formatted = CartItemAdd(
        product_id=uuid.uuid4(),
        variant_id=uuid.uuid4(),
        quantity=1,
        selected_customization="HEEL_SIZE: 2 inch",
        unit_price=Decimal("295.00"),
    )
    assert item_formatted.selected_customization == "HEEL_SIZE: 2 inch"


def test_invalid_heel_customization():
    """Verify arbitrary heel options are strictly rejected."""
    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=1,
            selected_customization="5 inch",
            unit_price=Decimal("295.00"),
        )

    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=1,
            selected_customization="platform stiletto",
            unit_price=Decimal("295.00"),
        )


def test_quantity_boundaries():
    """Verify quantity must be between 1 and 10 pairs."""
    # Valid quantity
    item = CartItemAdd(
        product_id=uuid.uuid4(),
        variant_id=uuid.uuid4(),
        quantity=5,
        unit_price=Decimal("380.00"),
    )
    assert item.quantity == 5

    # Zero or negative quantity
    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=0,
            unit_price=Decimal("380.00"),
        )

    # Exceeding maximum cap (10)
    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=11,
            unit_price=Decimal("380.00"),
        )


def test_unit_price_validation():
    """Verify unit price must be positive."""
    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=1,
            unit_price=Decimal("-10.00"),
        )

    with pytest.raises(ValidationError):
        CartItemAdd(
            product_id=uuid.uuid4(),
            variant_id=uuid.uuid4(),
            quantity=1,
            unit_price=Decimal("0.00"),
        )


def test_cart_merge_request_validation():
    """Verify guest session ID validation for cart merge."""
    req = CartMergeRequest(guest_session_id="guest-sess-abc-123")
    assert req.guest_session_id == "guest-sess-abc-123"

    with pytest.raises(ValidationError):
        CartMergeRequest(guest_session_id="")
