"""
Inventory Service API Routes.
Exposes real-time availability checks, stock reservations, and administrative stock operations.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_admin_claims
from app.schemas.inventory import (
    InventoryAvailabilityResponse,
    InventoryCreate,
    InventoryMovementResponse,
    InventoryResponse,
    PaginatedInventoryResponse,
    ReservationConfirmRequest,
    ReservationCreateRequest,
    ReservationReleaseRequest,
    ReservationResponse,
    StockAdjustmentRequest,
    ThresholdUpdateRequest,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ============================================================
# Availability & Cart Reservation Endpoints
# ============================================================

@router.get(
    "/variant/{variant_id}",
    response_model=InventoryAvailabilityResponse,
    summary="Get real-time stock availability for a footwear variant",
)
async def get_variant_availability(
    variant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Check stock and availability flags (in-stock, low-stock) for a specific footwear size/color."""
    svc = InventoryService(db)
    return await svc.get_variant_availability(variant_id)


@router.get(
    "/product/{product_id}",
    response_model=List[InventoryAvailabilityResponse],
    summary="Get real-time stock availability for all variants of a product",
)
async def get_product_availability(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve availability matrix across all shoe sizes and colors for a product."""
    svc = InventoryService(db)
    return await svc.get_product_availability(product_id)


@router.post(
    "/reserve",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve stock for checkout or cart hold",
)
async def reserve_stock(
    req: ReservationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Atomically hold stock using PostgreSQL row locks to prevent race conditions.
    Reservation automatically expires if not confirmed within duration.
    """
    svc = InventoryService(db)
    return await svc.reserve_stock(req)


@router.post(
    "/release",
    status_code=status.HTTP_200_OK,
    summary="Release stock hold",
)
async def release_reservation(
    req: ReservationReleaseRequest,
    db: AsyncSession = Depends(get_db),
):
    """Release active reservation and return stock to available pool."""
    svc = InventoryService(db)
    released = await svc.release_reservation(req)
    return {"success": released, "message": "Reservation released."}


@router.post(
    "/confirm",
    status_code=status.HTTP_200_OK,
    summary="Confirm reservation and commit stock reduction upon purchase",
)
async def confirm_reservation(
    req: ReservationConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """Finalize purchase and record sale in inventory audit ledger."""
    svc = InventoryService(db)
    confirmed = await svc.confirm_reservation(req)
    return {"success": confirmed, "message": "Reservation confirmed and stock updated."}


# ============================================================
# Administrative Endpoints
# ============================================================

@router.get(
    "/admin/list",
    response_model=PaginatedInventoryResponse,
    summary="Admin: Paginated inventory directory with low-stock filtering",
)
async def admin_list_inventory(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by SKU"),
    is_low_stock: Optional[bool] = Query(None, description="Filter items at or below threshold"),
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Admin view of all stock levels with search and low-stock filters."""
    svc = InventoryService(db)
    return await svc.admin_list_inventory(
        page=page, size=size, search=search, is_low_stock=is_low_stock
    )


@router.post(
    "/admin",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Initialize inventory record for a variant SKU",
)
async def admin_create_inventory(
    req: InventoryCreate,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Initialize stock tracking for a newly created variant SKU."""
    svc = InventoryService(db)
    return await svc.admin_create_inventory(req)


@router.patch(
    "/admin/{inventory_id}/stock",
    response_model=InventoryResponse,
    summary="Admin: Restock or adjust stock quantity",
)
async def admin_adjust_stock(
    inventory_id: uuid.UUID,
    req: StockAdjustmentRequest,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Perform transactional restock or stock adjustment with reason logged to movement ledger."""
    svc = InventoryService(db)
    return await svc.admin_adjust_stock(inventory_id, req)


@router.patch(
    "/admin/{inventory_id}/threshold",
    response_model=InventoryResponse,
    summary="Admin: Update low stock threshold",
)
async def admin_update_threshold(
    inventory_id: uuid.UUID,
    req: ThresholdUpdateRequest,
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Update threshold when low-stock alerts are triggered."""
    svc = InventoryService(db)
    return await svc.admin_update_threshold(inventory_id, req)


@router.get(
    "/admin/{inventory_id}/movements",
    response_model=List[InventoryMovementResponse],
    summary="Admin: Audit ledger of stock movements",
)
async def admin_get_movements(
    inventory_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Inspect immutable audit history of all restocks, reservations, and sales."""
    svc = InventoryService(db)
    return await svc.admin_get_movements(inventory_id, limit=limit)


@router.post(
    "/admin/cleanup-expired",
    summary="Admin: Release all expired reservations",
)
async def admin_cleanup_expired(
    admin: dict = Depends(get_current_admin_claims),
    db: AsyncSession = Depends(get_db),
):
    """Trigger sweep of expired reservations."""
    svc = InventoryService(db)
    count = await svc.release_expired()
    return {"released_count": count}
