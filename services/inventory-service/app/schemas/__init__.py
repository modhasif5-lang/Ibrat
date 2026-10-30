"""
Inventory Service Schemas Package.
"""

from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryAvailabilityResponse,
    PaginatedInventoryResponse,
    StockAdjustmentRequest,
    ThresholdUpdateRequest,
    ReservationCreateRequest,
    ReservationResponse,
    ReservationReleaseRequest,
    ReservationConfirmRequest,
    InventoryMovementResponse,
)

__all__ = [
    "InventoryCreate",
    "InventoryResponse",
    "InventoryAvailabilityResponse",
    "PaginatedInventoryResponse",
    "StockAdjustmentRequest",
    "ThresholdUpdateRequest",
    "ReservationCreateRequest",
    "ReservationResponse",
    "ReservationReleaseRequest",
    "ReservationConfirmRequest",
    "InventoryMovementResponse",
]
