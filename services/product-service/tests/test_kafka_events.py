"""
Unit tests for Product Service Kafka events and producer failure tolerance.
"""

import asyncio
from app.core.kafka_producer import KafkaEventProducer
from app.schemas.events import (
    DomainEvent,
    ProductCreatedEventPayload,
    ProductDeletedEventPayload,
    ReviewCreatedEventPayload,
)


def test_product_created_event_payload():
    """Verify serialization of product.created domain event."""
    payload = ProductCreatedEventPayload(
        id="prod-001",
        name="Aurelia Pump",
        slug="aurelia-pump",
        description="Silk satin pump",
        base_price=380.0,
        effective_price=380.0,
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["36", "37", "38"],
        colors=["Champagne Gold"],
    )

    event = DomainEvent(
        event_type="product.created",
        producer="product-service",
        payload=payload.model_dump(),
    )

    assert event.event_type == "product.created"
    assert event.producer == "product-service"
    assert event.payload["name"] == "Aurelia Pump"
    assert "2 inch" in event.payload["heel_sizes"]


def test_review_created_event_payload():
    """Verify serialization of review.created domain event."""
    payload = ReviewCreatedEventPayload(
        review_id="rev-001",
        product_id="prod-001",
        user_id="user-001",
        rating=5,
        new_average_rating=4.9,
        review_count=10,
    )

    event = DomainEvent(
        event_type="review.created",
        payload=payload.model_dump(),
    )

    assert event.payload["rating"] == 5
    assert event.payload["new_average_rating"] == 4.9


def test_producer_offline_fail_open():
    """Verify producer gracefully fails open when broker is disconnected."""
    async def _test():
        producer = KafkaEventProducer()
        event = DomainEvent(
            event_type="product.deleted",
            payload={"product_id": "prod-001"},
        )
        # When offline, publish returns False without raising an exception
        success = await producer.publish("product.events", event)
        assert success is False

    asyncio.run(_test())
