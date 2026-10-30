"""Initial Inventory Service Schema

Revision ID: 0001_initial_inventory_schema
Revises: 
Create Date: 2026-10-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "0001_initial_inventory_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Inventory
    op.create_table(
        "inventory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("variant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("available_quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("low_stock_threshold", sa.Integer(), server_default="5", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_variant_id", "inventory", ["variant_id"], unique=True)
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"])
    op.create_index("ix_inventory_sku", "inventory", ["sku"], unique=True)

    # 2. Inventory Movements
    op.create_table(
        "inventory_movements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("inventory_id", UUID(as_uuid=True), sa.ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity_change", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_movements_inventory_id", "inventory_movements", ["inventory_id"])

    # 3. Reservations
    op.create_table(
        "reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("inventory_id", UUID(as_uuid=True), sa.ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cart_id", UUID(as_uuid=True), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reservations_inventory_id", "reservations", ["inventory_id"])
    op.create_index("ix_reservations_cart_id", "reservations", ["cart_id"])


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("inventory_movements")
    op.drop_table("inventory")
