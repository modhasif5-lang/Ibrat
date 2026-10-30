"""
Unit tests for Inventory Service validation schemas.
"""

import uuid
import pytest
from pydantic import ValidationError

from app.schemas.inventory import (
    InventoryCreate,
    ReservationCreateRequest,
    StockAdjustmentRequest,
    ThresholdUpdateRequest,
)


def test_stock_adjustment_schema():
    """Verify adjustment validation requires valid movement types."""
    valid = StockAdjustmentRequest(quantity_change=20, type="RESTOCK", reason="Supplier delivery")
    assert valid.quantity_change == 20
    assert valid.type == "RESTOCK"

    # Invalid movement type
    with pytest.raises(ValidationError):
        StockAdjustmentRequest(quantity_change=10, type="INVALID_TYPE")


def test_reservation_request_schema():
    """Verify reservation requires positive quantity and valid duration."""
    var_id = uuid.uuid4()
    res = ReservationCreateRequest(
        variant_id=var_id,
        quantity=2,
        duration_minutes=30,
    )
    assert res.quantity == 2
    assert res.duration_minutes == 30

    # Quantity cannot be zero or negative
    with pytest.raises(ValidationError):
        ReservationCreateRequest(variant_id=var_id, quantity=0)

    with pytest.raises(ValidationError):
        ReservationCreateRequest(variant_id=var_id, quantity=-5)


def test_threshold_update_schema():
    """Verify threshold must be non-negative."""
    valid = ThresholdUpdateRequest(low_stock_threshold=5)
    assert valid.low_stock_threshold == 5

    with pytest.raises(ValidationError):
        ThresholdUpdateRequest(low_stock_threshold=-1)
