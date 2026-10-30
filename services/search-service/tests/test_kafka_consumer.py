"""
Unit tests for Search Service Kafka consumer.
Tests idempotency caching, event dispatching, and failure handling.
"""

import asyncio
from unittest.mock import AsyncMock, patch

from app.core.kafka_consumer import SearchEventConsumer
from app.schemas.search import ProductDocument


def test_consumer_idempotency_tracking():
    """Verify consumer tracks processed event IDs and skips duplicates."""
    consumer = SearchEventConsumer()
    assert not consumer.is_event_processed("evt-001")

    consumer.mark_event_processed("evt-001")
    assert consumer.is_event_processed("evt-001")
    assert not consumer.is_event_processed("evt-002")


def test_consumer_idempotency_lru_eviction():
    """Verify bounded memory usage in idempotency cache."""
    consumer = SearchEventConsumer()
    # Cache up to max limit + 5
    for i in range(5005):
        consumer.mark_event_processed(f"evt-{i}")

    # Oldest events should be evicted
    assert not consumer.is_event_processed("evt-0")
    assert consumer.is_event_processed("evt-5004")


def test_dispatch_product_created():
    """Verify product.created event maps to SearchService.index_product."""
    async def _test():
        consumer = SearchEventConsumer()
        payload = {
            "id": "prod-100",
            "name": "Velvet Pump",
            "slug": "velvet-pump",
            "description": "Luxury pump",
            "base_price": 250.0,
            "effective_price": 250.0,
            "heel_sizes": ["2 inch"],
            "sizes": ["38"],
            "colors": ["Ruby Red"],
            "is_active": True,
            "is_in_stock": True,
        }

        with patch("app.services.search_service.SearchService.index_product", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = True
            await consumer.dispatch_event("product.created", payload)
            mock_index.assert_called_once()
            called_doc = mock_index.call_args[0][0]
            assert isinstance(called_doc, ProductDocument)
            assert called_doc.id == "prod-100"

    asyncio.run(_test())


def test_dispatch_product_deleted():
    """Verify product.deleted event calls SearchService.delete_product."""
    async def _test():
        consumer = SearchEventConsumer()
        with patch("app.services.search_service.SearchService.delete_product", new_callable=AsyncMock) as mock_del:
            mock_del.return_value = True
            await consumer.dispatch_event("product.deleted", {"product_id": "prod-100"})
            mock_del.assert_called_once_with("prod-100")

    asyncio.run(_test())


def test_dispatch_inventory_updated():
    """Verify inventory.updated event calls SearchService.update_product_partial."""
    async def _test():
        consumer = SearchEventConsumer()
        with patch("app.services.search_service.SearchService.update_product_partial", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = True
            await consumer.dispatch_event(
                "inventory.updated",
                {"product_id": "prod-100", "is_in_stock": False},
            )
            mock_update.assert_called_once_with("prod-100", {"is_in_stock": False})

    asyncio.run(_test())


def test_dispatch_review_created():
    """Verify review.created event updates rating statistics in SearchService."""
    async def _test():
        consumer = SearchEventConsumer()
        with patch("app.services.search_service.SearchService.update_product_partial", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = True
            await consumer.dispatch_event(
                "review.created",
                {
                    "product_id": "prod-100",
                    "new_average_rating": 4.8,
                    "review_count": 12,
                },
            )
            mock_update.assert_called_once_with(
                "prod-100", {"average_rating": 4.8, "review_count": 12}
            )

    asyncio.run(_test())
