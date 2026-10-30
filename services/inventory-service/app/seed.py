"""
Inventory Service Seed Script.
Provisions initial stock balances and movements for luxury footwear variant SKUs.
Run via: python -m app.seed
"""

import asyncio
import logging
import uuid
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.inventory import Inventory, InventoryMovement

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed-inventory-service")

# Standard luxury footwear catalog SKUs and stock quantities
DEFAULT_SKU_STOCK = [
    # Aurelia Crystal Satin Pump
    ("IBR-AUR-GLD-36", 18, 5),
    ("IBR-AUR-GLD-37", 25, 5),
    ("IBR-AUR-GLD-38", 30, 5),
    ("IBR-AUR-GLD-39", 20, 5),
    ("IBR-AUR-GLD-40", 12, 5),
    ("IBR-AUR-EMR-37", 8, 5),
    ("IBR-AUR-EMR-38", 3, 5),   # Low stock demonstration item (3 <= 5)
    ("IBR-AUR-EMR-39", 6, 5),
    # Seraphina Nappa Ankle-Strap Heel
    ("IBR-SER-BLK-36", 15, 5),
    ("IBR-SER-BLK-37", 22, 5),
    ("IBR-SER-BLK-38", 28, 5),
    ("IBR-SER-BLK-39", 14, 5),
    ("IBR-SER-NUD-37", 10, 5),
    ("IBR-SER-NUD-38", 2, 5),   # Low stock demonstration item (2 <= 5)
    # Valentina Embellished Mule
    ("IBR-VAL-NAV-37", 14, 5),
    ("IBR-VAL-NAV-38", 16, 5),
    ("IBR-VAL-RUB-37", 8, 5),
    ("IBR-VAL-RUB-38", 12, 5),
    ("IBR-VAL-RUB-39", 4, 5),   # Low stock demonstration item (4 <= 5)
    # Celeste Pointed Toe Flat
    ("IBR-CEL-IVR-36", 20, 5),
    ("IBR-CEL-IVR-37", 25, 5),
    ("IBR-CEL-IVR-38", 35, 5),
    ("IBR-CEL-IVR-39", 18, 5),
    ("IBR-CEL-ROS-38", 15, 5),
    # Camilla Pearl Slingback
    ("IBR-CAM-WHT-36", 12, 5),
    ("IBR-CAM-WHT-37", 20, 5),
    ("IBR-CAM-WHT-38", 22, 5),
    ("IBR-CAM-WHT-39", 15, 5),
    ("IBR-CAM-PNK-37", 10, 5),
    ("IBR-CAM-PNK-38", 8, 5),
    # Leela Royal Wedge
    ("IBR-LEE-GLD-36", 16, 5),
    ("IBR-LEE-GLD-37", 24, 5),
    ("IBR-LEE-GLD-38", 28, 5),
    ("IBR-LEE-GLD-39", 19, 5),
    ("IBR-LEE-GLD-40", 14, 5),
]


async def seed_inventory() -> None:
    """Populate inventory balances."""
    logger.info("Starting Inventory Service database seeding...")

    async with AsyncSessionLocal() as session:
        try:
            seeded_count = 0
            for sku, stock, threshold in DEFAULT_SKU_STOCK:
                stmt = select(Inventory).where(Inventory.sku == sku)
                existing = (await session.execute(stmt)).scalar_one_or_none()

                if not existing:
                    variant_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"variant.{sku}")
                    product_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"product.{sku.split('-')[1]}")

                    inv = Inventory(
                        variant_id=variant_id,
                        product_id=product_id,
                        sku=sku,
                        stock_quantity=stock,
                        reserved_quantity=0,
                        available_quantity=stock,
                        low_stock_threshold=threshold,
                    )
                    session.add(inv)
                    await session.flush()

                    movement = InventoryMovement(
                        inventory_id=inv.id,
                        quantity_change=stock,
                        type="RESTOCK",
                        reason="Initial launch batch restock",
                    )
                    session.add(movement)
                    seeded_count += 1

            await session.commit()
            logger.info(f"Seeded {seeded_count} SKU inventory balances with audit ledger movements.")
            logger.info("Inventory Service database seeding completed successfully.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding Inventory Service: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_inventory())
