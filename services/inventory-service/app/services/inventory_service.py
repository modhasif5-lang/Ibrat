"""
Inventory Service Business Logic Layer.
Handles real-time stock checks, locking reservations, stock adjustments, and movements.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
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
from app.core.kafka_producer import event_producer
from app.schemas.events import DomainEvent



class InventoryService:
    """Core domain service for stock tracking and reservations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InventoryRepository(db)

    def _to_response(self, inv: Inventory) -> InventoryResponse:
        """Map model to InventoryResponse with derived status flags."""
        is_in_stock = inv.available_quantity > 0
        is_low_stock = inv.available_quantity <= inv.low_stock_threshold
        return InventoryResponse(
            id=inv.id,
            variant_id=inv.variant_id,
            product_id=inv.product_id,
            sku=inv.sku,
            stock_quantity=inv.stock_quantity,
            reserved_quantity=inv.reserved_quantity,
            available_quantity=inv.available_quantity,
            low_stock_threshold=inv.low_stock_threshold,
            is_in_stock=is_in_stock,
            is_low_stock=is_low_stock,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
        )

    async def _publish_inventory_event(self, inv: Inventory):
        is_low = inv.available_quantity <= inv.low_stock_threshold
        payload = {
            "product_id": str(inv.product_id),
            "variant_id": str(inv.variant_id),
            "sku": inv.sku,
            "stock_quantity": inv.stock_quantity,
            "reserved_quantity": inv.reserved_quantity,
            "available_quantity": inv.available_quantity,
            "is_in_stock": inv.available_quantity > 0,
            "is_low_stock": is_low,
        }
        await event_producer.publish(
            topic="inventory.events",
            event=DomainEvent(
                event_type="inventory.updated",
                producer="inventory-service",
                payload=payload,
            ),
            key=str(inv.product_id),
        )
        if is_low:
            await event_producer.publish(
                topic="inventory.events",
                event=DomainEvent(
                    event_type="inventory.low_stock",
                    producer="inventory-service",
                    payload={
                        "product_id": str(inv.product_id),
                        "variant_id": str(inv.variant_id),
                        "sku": inv.sku,
                        "available_quantity": inv.available_quantity,
                        "threshold": inv.low_stock_threshold,
                    },
                ),
                key=str(inv.product_id),
            )

    # ============================================================
    # Availability Queries (Public / Shop)
    # ============================================================

    async def get_variant_availability(self, variant_id: uuid.UUID) -> InventoryAvailabilityResponse:
        """Retrieve real-time availability for a variant SKU."""
        inv = await self.repo.get_by_variant_id(variant_id)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory record for variant '{variant_id}' not found.",
            )

        return InventoryAvailabilityResponse(
            variant_id=inv.variant_id,
            sku=inv.sku,
            available_quantity=inv.available_quantity,
            is_in_stock=inv.available_quantity > 0,
            is_low_stock=inv.available_quantity <= inv.low_stock_threshold,
        )

    async def get_product_availability(self, product_id: uuid.UUID) -> List[InventoryAvailabilityResponse]:
        """Retrieve availability for all variant SKUs of a footwear product."""
        items = await self.repo.get_by_product_id(product_id)
        return [
            InventoryAvailabilityResponse(
                variant_id=i.variant_id,
                sku=i.sku,
                available_quantity=i.available_quantity,
                is_in_stock=i.available_quantity > 0,
                is_low_stock=i.available_quantity <= i.low_stock_threshold,
            )
            for i in items
        ]

    # ============================================================
    # Stock Reservations (Transactional with Row Locks)
    # ============================================================

    async def reserve_stock(self, req: ReservationCreateRequest) -> ReservationResponse:
        """
        Reserve stock for a footwear variant.
        Uses row-level locking (FOR UPDATE) to guarantee race condition safety.
        """
        inv = await self.repo.get_by_variant_id(req.variant_id, for_update=True)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory for variant '{req.variant_id}' not found.",
            )

        if inv.available_quantity < req.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for SKU '{inv.sku}'. Available: {inv.available_quantity}, Requested: {req.quantity}.",
            )

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=req.duration_minutes)
        reservation = await self.repo.create_reservation(
            inventory=inv,
            quantity=req.quantity,
            cart_id=req.cart_id,
            expires_at=expires_at,
        )

        return ReservationResponse.model_validate(reservation)

    async def release_reservation(self, req: ReservationReleaseRequest) -> bool:
        """Release active stock hold."""
        if req.reservation_id:
            res = await self.repo.get_reservation_by_id(req.reservation_id, for_update=True)
            if res:
                await self.repo.release_reservation(res)
                return True
        elif req.cart_id:
            reservations = await self.repo.get_active_reservations_by_cart(req.cart_id, for_update=True)
            for r in reservations:
                await self.repo.release_reservation(r)
            return True
        return False

    async def confirm_reservation(self, req: ReservationConfirmRequest) -> bool:
        """Permanently deduct stock when purchase succeeds."""
        res = await self.repo.get_reservation_by_id(req.reservation_id, for_update=True)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found.",
            )

        if res.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm reservation in status '{res.status}'.",
            )

        await self.repo.confirm_reservation(res, reference_id=req.reference_id)
        if res.inventory:
            await self._publish_inventory_event(res.inventory)
        return True

    async def release_expired(self) -> int:
        """Periodic cleanup task releasing expired reservations."""
        return await self.repo.release_expired_reservations()

    # ============================================================
    # Administration
    # ============================================================

    async def admin_list_inventory(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        is_low_stock: Optional[bool] = None,
    ) -> PaginatedInventoryResponse:
        items, total = await self.repo.list_inventory(
            page=page, size=size, search=search, is_low_stock=is_low_stock
        )
        responses = [self._to_response(i) for i in items]
        return PaginatedInventoryResponse(total=total, page=page, size=size, items=responses)

    async def admin_create_inventory(self, req: InventoryCreate) -> InventoryResponse:
        existing = await self.repo.get_by_sku(req.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Inventory record for SKU '{req.sku}' already exists.",
            )

        inv = await self.repo.create_inventory(
            variant_id=req.variant_id,
            product_id=req.product_id,
            sku=req.sku,
            stock_quantity=req.stock_quantity,
            low_stock_threshold=req.low_stock_threshold,
        )
        await self._publish_inventory_event(inv)
        return self._to_response(inv)

    async def admin_adjust_stock(
        self, inventory_id: uuid.UUID, req: StockAdjustmentRequest
    ) -> InventoryResponse:
        inv = await self.repo.get_by_id(inventory_id, for_update=True)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory record not found.",
            )

        if inv.stock_quantity + req.quantity_change < inv.reserved_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reduce stock below current active reserved quantity.",
            )

        updated = await self.repo.update_stock(
            inventory=inv,
            quantity_change=req.quantity_change,
            movement_type=req.type,
            reason=req.reason,
        )
        await self._publish_inventory_event(updated)
        return self._to_response(updated)

    async def admin_update_threshold(
        self, inventory_id: uuid.UUID, req: ThresholdUpdateRequest
    ) -> InventoryResponse:
        inv = await self.repo.get_by_id(inventory_id)
        if not inv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory record not found.",
            )

        updated = await self.repo.update_threshold(inv, req.low_stock_threshold)
        return self._to_response(updated)

    async def admin_get_movements(
        self, inventory_id: uuid.UUID, limit: int = 50
    ) -> List[InventoryMovementResponse]:
        movements = await self.repo.get_movements(inventory_id, limit=limit)
        return [InventoryMovementResponse.model_validate(m) for m in movements]
