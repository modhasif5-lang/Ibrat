"""
Kafka Domain Event Schemas for Inventory Service.
Publishes real-time stock updates and low-stock alerts to the search service and notification pipelines.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    """Standard envelope for all Ibrat asynchronous Kafka events."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    producer: str = "inventory-service"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any]


class InventoryUpdatedEventPayload(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    stock_quantity: int
    reserved_quantity: int
    available_quantity: int
    is_in_stock: bool
    is_low_stock: bool


class LowStockAlertEventPayload(BaseModel):
    product_id: str
    variant_id: str
    sku: str
    available_quantity: int
    threshold: int
