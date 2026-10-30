"""
Pydantic schemas for Cart Service.
Covers cart items, footwear customizations, quantities, subtotals, and validation against inventory.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


ALLOWED_HEEL_SIZES = {"1 inch", "2 inch", "3 inch"}


class CartItemBase(BaseModel):
    product_id: uuid.UUID
    variant_id: uuid.UUID
    quantity: int = Field(1, ge=1, le=10, description="Quantity of footwear variant (max 10 per item)")
    selected_customization: Optional[str] = Field(
        None,
        description="Footwear customization: strictly '1 inch', '2 inch', or '3 inch'",
    )

    @field_validator("selected_customization")
    @classmethod
    def validate_heel_customization(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            # Normalize if formatted as "HEEL_SIZE: 2 inch"
            val = clean.replace("HEEL_SIZE:", "").strip()
            if val not in ALLOWED_HEEL_SIZES:
                raise ValueError(
                    f"Invalid heel customization '{v}'. Permitted heel sizes are: {', '.join(sorted(ALLOWED_HEEL_SIZES))}."
                )
            return f"HEEL_SIZE: {val}"
        return v


class CartItemAdd(CartItemBase):
    """Payload to add an item to the shopping cart."""
    unit_price: Decimal = Field(..., gt=0, decimal_places=2, description="Price per unit in catalog currency")


class CartItemUpdate(BaseModel):
    """Payload to update quantity of an existing cart item."""
    quantity: int = Field(..., ge=1, le=10, description="New quantity (1-10)")


class CartItemResponse(BaseModel):
    """Response schema for a single cart item."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    variant_id: uuid.UUID
    quantity: int
    selected_customization: Optional[str] = None
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime


class CartResponse(BaseModel):
    """Full shopping cart response with items, total item count, and total price."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    items: List[CartItemResponse] = []
    total_items: int = 0
    total_price: Decimal = Decimal("0.00")
    created_at: datetime
    updated_at: datetime


class CartMergeRequest(BaseModel):
    """Payload to merge a guest session cart into the authenticated customer's cart."""
    guest_session_id: str = Field(..., min_length=1, description="Session ID of the guest cart to merge")


class CartValidationIssue(BaseModel):
    """Details of an item exceeding available inventory."""
    variant_id: uuid.UUID
    product_id: uuid.UUID
    requested_quantity: int
    available_quantity: int
    message: str


class CartValidationResponse(BaseModel):
    """Response indicating whether all cart items are currently available in stock."""
    is_valid: bool
    total_items: int
    issues: List[CartValidationIssue] = []
