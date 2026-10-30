"""
Unit tests for Inventory Service Kafka events and producer failure tolerance.
"""

import asyncio
from app.core.kafka_producer import KafkaEventProducer
from app.schemas.events import (
    DomainEvent,
    InventoryUpdatedEventPayload,
    LowStockAlertEventPayload,
)


def test_inventory_updated_event_payload():
    """Verify serialization of inventory.updated domain event."""
    payload = InventoryUpdatedEventPayload(
        product_id="prod-001",
        variant_id="var-001",
        sku="AUR-SAT-GLD-38",
        stock_quantity=15,
        reserved_quantity=2,
        available_quantity=13,
        is_in_stock=True,
        is_low_stock=False,
    )

    event = DomainEvent(
        event_type="inventory.updated",
        producer="inventory-service",
        payload=payload.model_dump(),
    )

    assert event.event_type == "inventory.updated"
    assert event.payload["available_quantity"] == 13
    assert event.payload["is_in_stock"] is True


def test_low_stock_alert_event_payload():
    """Verify serialization of inventory.low_stock domain event."""
    payload = LowStockAlertEventPayload(
        product_id="prod-001",
        variant_id="var-001",
        sku="AUR-SAT-GLD-38",
        available_quantity=2,
        threshold=3,
    )

    event = DomainEvent(
        event_type="inventory.low_stock",
        payload=payload.model_dump(),
    )

    assert event.payload["available_quantity"] == 2
    assert event.payload["threshold"] == 3


def test_inventory_producer_offline_fail_open():
    """Verify producer gracefully fails open when broker is disconnected."""
    async def _test():
        producer = KafkaEventProducer()
        event = DomainEvent(
            event_type="inventory.updated",
            payload={"variant_id": "var-001"},
        )
        success = await producer.publish("inventory.events", event)
        assert success is False

    asyncio.run(_test())
