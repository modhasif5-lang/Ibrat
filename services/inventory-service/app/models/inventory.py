"""
Inventory Service Database Models.
Covers real-time stock levels, stock reservations, and inventory audit movements.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Inventory(Base, UUIDMixin, TimestampMixin):
    """Stock tracking entity for a specific footwear variant."""

    __tablename__ = "inventory"

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, index=True, nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    movements: Mapped[List["InventoryMovement"]] = relationship(
        "InventoryMovement", back_populates="inventory", cascade="all, delete-orphan"
    )
    reservations: Mapped[List["Reservation"]] = relationship(
        "Reservation", back_populates="inventory", cascade="all, delete-orphan"
    )


class InventoryMovement(Base, UUIDMixin):
    """Audit log of stock movements (restocks, reservations, sales, adjustments)."""

    __tablename__ = "inventory_movements"

    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), index=True, nullable=False
    )
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # RESTOCK, RESERVATION, RELEASE, SALE, ADJUSTMENT
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="movements")


class Reservation(Base, UUIDMixin):
    """Temporary or confirmed stock reservations during shopping/checkout."""

    __tablename__ = "reservations"

    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), index=True, nullable=False
    )
    cart_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, CONFIRMED, RELEASED, EXPIRED
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="reservations")
