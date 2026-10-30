"""
Inventory Service Database Repository.
Implements transactional operations with row-level locks (with_for_update) to prevent overselling.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory, InventoryMovement, Reservation


class InventoryRepository:
    """Data access repository for inventory, stock transactions, and reservations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # Inventory Record Queries
    # ============================================================

    async def get_by_id(
        self, inventory_id: uuid.UUID, for_update: bool = False
    ) -> Optional[Inventory]:
        stmt = select(Inventory).where(Inventory.id == inventory_id)
        if for_update:
            stmt = stmt.with_for_update()
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_variant_id(
        self, variant_id: uuid.UUID, for_update: bool = False
    ) -> Optional[Inventory]:
        stmt = select(Inventory).where(Inventory.variant_id == variant_id)
        if for_update:
            stmt = stmt.with_for_update()
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_sku(
        self, sku: str, for_update: bool = False
    ) -> Optional[Inventory]:
        stmt = select(Inventory).where(Inventory.sku == sku.upper())
        if for_update:
            stmt = stmt.with_for_update()
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_product_id(self, product_id: uuid.UUID) -> List[Inventory]:
        stmt = select(Inventory).where(Inventory.product_id == product_id)
        return list((await self.db.execute(stmt)).scalars().all())

    async def create_inventory(
        self,
        variant_id: uuid.UUID,
        product_id: uuid.UUID,
        sku: str,
        stock_quantity: int = 0,
        low_stock_threshold: int = 5,
    ) -> Inventory:
        inv = Inventory(
            variant_id=variant_id,
            product_id=product_id,
            sku=sku.upper(),
            stock_quantity=stock_quantity,
            reserved_quantity=0,
            available_quantity=stock_quantity,
            low_stock_threshold=low_stock_threshold,
        )
        self.db.add(inv)
        await self.db.flush()

        # Initial ledger movement if stock > 0
        if stock_quantity > 0:
            m = InventoryMovement(
                inventory_id=inv.id,
                quantity_change=stock_quantity,
                type="RESTOCK",
                reason="Initial stock creation",
            )
            self.db.add(m)
            await self.db.flush()

        return inv

    async def update_stock(
        self,
        inventory: Inventory,
        quantity_change: int,
        movement_type: str,
        reference_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Inventory:
        """
        Transactional stock modification with audit ledger entry.
        quantity_change is signed (+ for restock, - for reduction).
        """
        inventory.stock_quantity += quantity_change
        inventory.available_quantity = inventory.stock_quantity - inventory.reserved_quantity

        movement = InventoryMovement(
            inventory_id=inventory.id,
            quantity_change=quantity_change,
            type=movement_type,
            reference_id=reference_id,
            reason=reason,
        )
        self.db.add(movement)
        await self.db.flush()
        return inventory

    async def update_threshold(self, inventory: Inventory, threshold: int) -> Inventory:
        inventory.low_stock_threshold = threshold
        await self.db.flush()
        return inventory

    async def list_inventory(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        is_low_stock: Optional[bool] = None,
    ) -> Tuple[List[Inventory], int]:
        offset = (page - 1) * size
        conditions = []

        if search:
            conditions.append(Inventory.sku.ilike(f"%{search.strip()}%"))
        if is_low_stock is True:
            conditions.append(Inventory.available_quantity <= Inventory.low_stock_threshold)
        elif is_low_stock is False:
            conditions.append(Inventory.available_quantity > Inventory.low_stock_threshold)

        count_stmt = select(func.count(Inventory.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = select(Inventory)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(desc(Inventory.created_at)).offset(offset).limit(size)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    # ============================================================
    # Reservations Management
    # ============================================================

    async def create_reservation(
        self,
        inventory: Inventory,
        quantity: int,
        cart_id: Optional[uuid.UUID],
        expires_at: datetime,
    ) -> Reservation:
        """Reserve available stock using row-level lock."""
        inventory.reserved_quantity += quantity
        inventory.available_quantity = inventory.stock_quantity - inventory.reserved_quantity

        reservation = Reservation(
            inventory_id=inventory.id,
            cart_id=cart_id,
            quantity=quantity,
            status="ACTIVE",
            expires_at=expires_at,
        )
        self.db.add(reservation)

        movement = InventoryMovement(
            inventory_id=inventory.id,
            quantity_change=-quantity,
            type="RESERVATION",
            reference_id=str(cart_id) if cart_id else None,
            reason="Cart hold reservation",
        )
        self.db.add(movement)
        await self.db.flush()
        return reservation

    async def get_reservation_by_id(
        self, reservation_id: uuid.UUID, for_update: bool = False
    ) -> Optional[Reservation]:
        stmt = select(Reservation).where(Reservation.id == reservation_id)
        if for_update:
            stmt = stmt.with_for_update()
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_active_reservations_by_cart(
        self, cart_id: uuid.UUID, for_update: bool = False
    ) -> List[Reservation]:
        stmt = select(Reservation).where(
            Reservation.cart_id == cart_id,
            Reservation.status == "ACTIVE",
        )
        if for_update:
            stmt = stmt.with_for_update()
        return list((await self.db.execute(stmt)).scalars().all())

    async def release_reservation(self, reservation: Reservation) -> None:
        """Release reservation and restore available quantity."""
        if reservation.status != "ACTIVE":
            return

        inv = await self.get_by_id(reservation.inventory_id, for_update=True)
        if inv:
            inv.reserved_quantity = max(0, inv.reserved_quantity - reservation.quantity)
            inv.available_quantity = inv.stock_quantity - inv.reserved_quantity

            movement = InventoryMovement(
                inventory_id=inv.id,
                quantity_change=reservation.quantity,
                type="RELEASE",
                reference_id=str(reservation.id),
                reason="Reservation released or expired",
            )
            self.db.add(movement)

        reservation.status = "RELEASED"
        await self.db.flush()

    async def confirm_reservation(
        self, reservation: Reservation, reference_id: Optional[str] = None
    ) -> None:
        """Commit reservation upon completed checkout (permanently decrements stock)."""
        if reservation.status != "ACTIVE":
            return

        inv = await self.get_by_id(reservation.inventory_id, for_update=True)
        if inv:
            inv.stock_quantity -= reservation.quantity
            inv.reserved_quantity = max(0, inv.reserved_quantity - reservation.quantity)
            inv.available_quantity = inv.stock_quantity - inv.reserved_quantity

            movement = InventoryMovement(
                inventory_id=inv.id,
                quantity_change=-reservation.quantity,
                type="SALE",
                reference_id=reference_id or str(reservation.id),
                reason="Order checkout confirmed",
            )
            self.db.add(movement)

        reservation.status = "CONFIRMED"
        await self.db.flush()

    async def release_expired_reservations(self) -> int:
        """Release all active reservations whose expiry timestamp has passed."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Reservation)
            .where(
                Reservation.status == "ACTIVE",
                Reservation.expires_at <= now,
            )
            .with_for_update()
        )
        expired_reservations = list((await self.db.execute(stmt)).scalars().all())
        for res in expired_reservations:
            await self.release_reservation(res)
        return len(expired_reservations)

    async def get_movements(
        self, inventory_id: uuid.UUID, limit: int = 50
    ) -> List[InventoryMovement]:
        stmt = (
            select(InventoryMovement)
            .where(InventoryMovement.inventory_id == inventory_id)
            .order_by(desc(InventoryMovement.created_at))
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())
