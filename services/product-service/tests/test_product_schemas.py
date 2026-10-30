"""
Unit tests for Product Service schemas and footwear domain validation.
"""

import uuid
from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.schemas.product import (
    CategoryCreate,
    CustomizationOptionCreate,
    ProductCreate,
    ProductVariantCreate,
    ReviewCreate,
)


def test_heel_customization_validation():
    """Verify footwear customization is strictly constrained to 1, 2, or 3-inch heels."""
    # Valid options
    opt1 = CustomizationOptionCreate(type="HEEL_SIZE", value="1 inch")
    opt2 = CustomizationOptionCreate(type="HEEL_SIZE", value="2 inch")
    opt3 = CustomizationOptionCreate(type="HEEL_SIZE", value="3 inch")
    assert opt1.value == "1 inch"
    assert opt2.value == "2 inch"
    assert opt3.value == "3 inch"

    # Invalid arbitrary heel option
    with pytest.raises(ValidationError):
        CustomizationOptionCreate(type="HEEL_SIZE", value="5 inch")

    with pytest.raises(ValidationError):
        CustomizationOptionCreate(type="HEEL_SIZE", value="platform")


def test_review_rating_validation():
    """Verify reviews enforce ratings between 1 and 5 stars."""
    # Valid ratings
    r1 = ReviewCreate(rating=1, comment="Poor fit around toe box.")
    r5 = ReviewCreate(rating=5, comment="Exceptional Italian silk satin finish.")
    assert r1.rating == 1
    assert r5.rating == 5

    # Out of bounds rating (0 or 6)
    with pytest.raises(ValidationError):
        ReviewCreate(rating=0, comment="Not allowed")

    with pytest.raises(ValidationError):
        ReviewCreate(rating=6, comment="Too high")


def test_product_create_schema():
    """Verify product requires category and non-negative base price."""
    cat_id = uuid.uuid4()
    p = ProductCreate(
        name="Aurelia Pump",
        description="Luxury silk satin stiletto.",
        category_id=cat_id,
        base_price=Decimal("380.00"),
    )
    assert p.base_price == Decimal("380.00")

    # Negative price rejected
    with pytest.raises(ValidationError):
        ProductCreate(
            name="Negative Price Shoe",
            description="Test",
            category_id=cat_id,
            base_price=Decimal("-50.00"),
        )
