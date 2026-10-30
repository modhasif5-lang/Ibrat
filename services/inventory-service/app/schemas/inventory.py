"""
Pydantic validation schemas for Inventory Service.
Covers real-time stock availability, reservations, and inventory movements.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Inventory Core Schemas
# ============================================================

class InventoryBase(BaseModel):
    variant_id: uuid.UUID
    product_id: uuid.UUID
    sku: str = Field(..., max_length=100)
    stock_quantity: int = Field(0, ge=0)
    low_stock_threshold: int = Field(5, ge=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reserved_quantity: int
    available_quantity: int
    is_in_stock: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class InventoryAvailabilityResponse(BaseModel):
    """Concise real-time availability indicator for footwear product pages."""
    variant_id: uuid.UUID
    sku: str
    available_quantity: int
    is_in_stock: bool
    is_low_stock: bool


class PaginatedInventoryResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[InventoryResponse]


# ============================================================
# Stock Adjustments & Restocking
# ============================================================

class StockAdjustmentRequest(BaseModel):
    """Payload for manual or restock inventory adjustments."""
    quantity_change: int = Field(..., description="Positive for restock, negative for write-off")
    type: str = Field("RESTOCK", pattern="^(RESTOCK|ADJUSTMENT|DAMAGE|RETURN)$")
    reason: Optional[str] = Field(None, max_length=255)


class ThresholdUpdateRequest(BaseModel):
    """Update low stock alert threshold."""
    low_stock_threshold: int = Field(..., ge=0)


# ============================================================
# Reservations (Cart / Checkout Stock Holds)
# ============================================================

class ReservationCreateRequest(BaseModel):
    """Payload to reserve stock while customer browses or checks out."""
    variant_id: uuid.UUID
    quantity: int = Field(1, ge=1)
    cart_id: Optional[uuid.UUID] = None
    duration_minutes: int = Field(15, ge=1, le=120, description="Hold duration in minutes")


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inventory_id: uuid.UUID
    cart_id: Optional[uuid.UUID] = None
    quantity: int
    status: str
    expires_at: datetime
    created_at: datetime


class ReservationReleaseRequest(BaseModel):
    """Payload to release an existing reservation."""
    reservation_id: Optional[uuid.UUID] = None
    cart_id: Optional[uuid.UUID] = None


class ReservationConfirmRequest(BaseModel):
    """Payload to permanently commit a reservation upon order checkout."""
    reservation_id: uuid.UUID
    reference_id: Optional[str] = Field(None, max_length=100)


# ============================================================
# Inventory Movements Audit Log
# ============================================================

class InventoryMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inventory_id: uuid.UUID
    quantity_change: int
    type: str
    reference_id: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
