"""
User Service Seed Script.
Provisions default administrator and demo customer accounts.
Run via: python -m app.seed
"""

import asyncio
import logging
from sqlalchemy import select

from app.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserPreference, Wishlist, Notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("seed-user-service")
settings = get_settings()


async def seed_users() -> None:
    """Seed initial administrator and demo customer."""
    logger.info("Starting User Service database seeding...")

    async with AsyncSessionLocal() as session:
        try:
            # 1. Seed Administrator
            admin_stmt = select(User).where(User.email == settings.ADMIN_EMAIL.lower())
            admin_res = await session.execute(admin_stmt)
            admin = admin_res.scalar_one_or_none()

            if not admin:
                admin_hashed = hash_password(settings.ADMIN_PASSWORD)
                admin = User(
                    email=settings.ADMIN_EMAIL.lower(),
                    hashed_password=admin_hashed,
                    full_name="Ibrat Administrator",
                    phone="+1234567890",
                    role="ADMIN",
                    is_active=True,
                    is_verified=True,
                )
                session.add(admin)
                await session.flush()

                # Add admin wishlist and preferences
                session.add_all([
                    Wishlist(user_id=admin.id),
                    UserPreference(user_id=admin.id),
                    Notification(
                        user_id=admin.id,
                        title="Admin Console Initialized",
                        message="Your Ibrat administrator account is active. Manage users, catalog, and inventory.",
                        type="ALERT",
                    ),
                ])
                logger.info(f"Created default admin user: {settings.ADMIN_EMAIL}")
            else:
                logger.info(f"Admin user already exists: {settings.ADMIN_EMAIL}")

            # 2. Seed Demo Customer
            demo_email = "customer@ibrat.com"
            cust_stmt = select(User).where(User.email == demo_email)
            cust_res = await session.execute(cust_stmt)
            customer = cust_res.scalar_one_or_none()

            if not customer:
                cust_hashed = hash_password("Customer@12345")
                customer = User(
                    email=demo_email,
                    hashed_password=cust_hashed,
                    full_name="Sophia Loren",
                    phone="+1987654321",
                    role="CUSTOMER",
                    is_active=True,
                    is_verified=True,
                )
                session.add(customer)
                await session.flush()

                # Add customer wishlist, preferences, and welcome notification
                session.add_all([
                    Wishlist(user_id=customer.id),
                    UserPreference(
                        user_id=customer.id,
                        preferred_size="38",
                        preferred_heel="2 inch",
                        preferred_colors="Champagne Gold, Blush Pink",
                        newsletter_subscribed=True,
                    ),
                    Notification(
                        user_id=customer.id,
                        title="Welcome to Ibrat Footwear",
                        message="Enjoy hand-crafted luxury footwear designed for timeless sophistication and personalized heel comfort.",
                        type="INFO",
                    ),
                ])
                logger.info(f"Created demo customer: {demo_email}")
            else:
                logger.info(f"Demo customer already exists: {demo_email}")

            await session.commit()
            logger.info("User Service seeding completed successfully.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during User Service seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_users())
