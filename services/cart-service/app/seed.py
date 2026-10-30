"""
Cart Service Seed Script.
Seeds demo cart items with luxury footwear customizations for development.
Run via: python -m app.seed
"""

import asyncio
import logging
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.cart import Cart, CartItem

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed-cart-service")

# Customer user ID from user-service seed
DEMO_CUSTOMER_ID = uuid.UUID("u1000000-0000-0000-0000-000000000002")

# Product and Variant IDs from product-service seed
AURELIA_PRODUCT_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
AURELIA_VARIANT_38_GOLD = uuid.UUID("v1000000-0000-0000-0000-000000000003")

SERAPHINA_PRODUCT_ID = uuid.UUID("a1000000-0000-0000-0000-000000000002")
SERAPHINA_VARIANT_38_BLACK = uuid.UUID("v1000000-0000-0000-0000-000000000009")


async def seed_cart_service():
    """Seed demo cart for customer."""
    logger.info("Seeding cart-service database...")
    async with async_session_factory() as session:
        # Check if cart already exists for demo customer
        from sqlalchemy import select
        res = await session.execute(select(Cart).where(Cart.user_id == DEMO_CUSTOMER_ID))
        existing_cart = res.scalar_one_or_none()

        if not existing_cart:
            demo_cart = Cart(
                id=uuid.UUID("d1000000-0000-0000-0000-000000000001"),
                user_id=DEMO_CUSTOMER_ID,
                session_id=None,
            )
            session.add(demo_cart)
            await session.flush()

            # Add Aurelia Pump with 2-inch heel customization
            item1 = CartItem(
                id=uuid.UUID("d1000000-0000-0000-0000-000000000011"),
                cart_id=demo_cart.id,
                product_id=AURELIA_PRODUCT_ID,
                variant_id=AURELIA_VARIANT_38_GOLD,
                quantity=1,
                selected_customization="HEEL_SIZE: 2 inch",
                unit_price=Decimal("380.00"),
            )
            # Add Seraphina Ankle-Strap with 3-inch heel customization
            item2 = CartItem(
                id=uuid.UUID("d1000000-0000-0000-0000-000000000012"),
                cart_id=demo_cart.id,
                product_id=SERAPHINA_PRODUCT_ID,
                variant_id=SERAPHINA_VARIANT_38_BLACK,
                quantity=1,
                selected_customization="HEEL_SIZE: 3 inch",
                unit_price=Decimal("295.00"),
            )
            session.add_all([item1, item2])
            await session.commit()
            logger.info("Created demo customer cart with 2 footwear items.")
        else:
            logger.info("Demo cart already exists.")


if __name__ == "__main__":
    asyncio.run(seed_cart_service())
