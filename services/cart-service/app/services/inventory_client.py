"""
HTTP client for cross-service inventory availability checks.
Communicates strictly via REST with Inventory Service (:8005), maintaining complete database isolation.
"""

import logging
import uuid
from typing import Optional, Tuple
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class InventoryClient:
    """Handles REST-based inventory availability checks for the cart."""

    def __init__(self):
        self.base_url = settings.INVENTORY_SERVICE_URL.rstrip("/")

    async def get_available_quantity(self, variant_id: uuid.UUID) -> Optional[int]:
        """Query inventory-service for available quantity of a footwear variant."""
        url = f"{self.base_url}/inventory/variant/{variant_id}"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return int(data.get("available_quantity", 0))
                elif response.status_code == 404:
                    logger.warning(f"Variant {variant_id} not found in inventory service.")
                    return 0
                else:
                    logger.warning(
                        f"Inventory service returned status {response.status_code} for variant {variant_id}."
                    )
                    return None
        except Exception as e:
            logger.warning(
                f"Could not reach inventory service at {url}: {e}. Proceeding with optimistic fallback."
            )
            return None

    async def check_availability(self, variant_id: uuid.UUID, requested_quantity: int) -> Tuple[bool, int]:
        """
        Validate whether requested quantity is in stock.
        Returns (is_available, stock_count).
        If inventory service is unreachable, optimistically allows the action with warning.
        """
        stock = await self.get_available_quantity(variant_id)
        if stock is None:
            # Service unreachable in local isolated testing; optimistic fallback
            return True, requested_quantity

        is_available = stock >= requested_quantity
        return is_available, stock


inventory_client = InventoryClient()
