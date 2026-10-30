"""
Kafka Event Consumer for Search Service.
Consumes product, inventory, and review domain events to maintain Elasticsearch index consistency.
Implements bounded in-memory idempotency deduplication, retry handling, and Dead-Letter Queue (DLQ) routing.
"""

import asyncio
from collections import OrderedDict
import json
import logging
from typing import Any, Dict, Optional, Set
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import get_settings
from app.schemas.search import ProductDocument
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)
settings = get_settings()

MAX_PROCESSED_EVENTS_CACHE = 5000
MAX_RETRIES = 3


class SearchEventConsumer:
    """Consumes domain events to keep Elasticsearch eventually consistent."""

    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.dlq_producer: Optional[AIOKafkaProducer] = None
        self._running: bool = False
        self._processed_events: OrderedDict[str, bool] = OrderedDict()
        self._consume_task: Optional[asyncio.Task] = None

    def is_event_processed(self, event_id: str) -> bool:
        """Check whether event has already been handled (idempotent guarantee)."""
        return event_id in self._processed_events

    def mark_event_processed(self, event_id: str):
        """Record event ID in bounded LRU cache."""
        self._processed_events[event_id] = True
        if len(self._processed_events) > MAX_PROCESSED_EVENTS_CACHE:
            self._processed_events.popitem(last=False)

    async def start(self):
        """Start async consumer loop and DLQ producer."""
        try:
            self.consumer = AIOKafkaConsumer(
                "product.events",
                "inventory.events",
                "review.events",
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id="search-service-indexer-group",
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            await self.consumer.start()

            self.dlq_producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            )
            await self.dlq_producer.start()

            self._running = True
            logger.info("Kafka search index event consumer started successfully.")
            self._consume_task = asyncio.create_task(self._consume_loop())
        except Exception as e:
            logger.warning(f"Kafka consumer connection deferred (broker not ready): {e}")

    async def stop(self):
        """Gracefully stop consumer and DLQ producer."""
        self._running = False
        if self._consume_task:
            self._consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
        if self.dlq_producer:
            await self.dlq_producer.stop()
        logger.info("Kafka search index event consumer stopped.")

    async def _consume_loop(self):
        """Main listening and dispatch loop."""
        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                topic = msg.topic
                event_data: Dict[str, Any] = msg.value or {}
                event_id = event_data.get("event_id")
                event_type = event_data.get("event_type")

                if not event_id or not event_type:
                    logger.warning(f"Malformed event received on {topic}: {event_data}")
                    continue

                if self.is_event_processed(event_id):
                    logger.debug(f"Skipping already-processed event {event_id} ({event_type}).")
                    continue

                success = await self._process_with_retry(topic, event_data)
                if success:
                    self.mark_event_processed(event_id)
                else:
                    await self._route_to_dlq(topic, event_data)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Kafka consumer loop: {e}")

    async def _process_with_retry(self, topic: str, event_data: Dict[str, Any]) -> bool:
        """Retry event dispatching up to MAX_RETRIES before failing to DLQ."""
        event_type = event_data.get("event_type")
        payload = event_data.get("payload", {})

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                await self.dispatch_event(event_type, payload)
                logger.info(f"Successfully processed {event_type} on attempt {attempt}.")
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed for {event_type}: {e}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(0.5 * attempt)
        return False

    async def dispatch_event(self, event_type: str, payload: Dict[str, Any]):
        """Route event payload to appropriate Elasticsearch index operation."""
        svc = SearchService()

        # Product events
        if event_type in ("product.created", "product.updated"):
            doc = ProductDocument.model_validate(payload)
            await svc.index_product(doc)
            logger.info(f"Indexed product document '{doc.id}' from Kafka {event_type} event.")

        elif event_type == "product.deleted":
            product_id = payload.get("product_id")
            if product_id:
                await svc.delete_product(product_id)
                logger.info(f"Deleted product document '{product_id}' from Kafka event.")

        # Inventory stock events
        elif event_type == "inventory.updated":
            product_id = payload.get("product_id")
            is_in_stock = payload.get("is_in_stock", True)
            if product_id:
                await svc.update_product_partial(product_id, {"is_in_stock": is_in_stock})
                logger.info(f"Updated product '{product_id}' stock status to {is_in_stock}.")

        # Review rating events
        elif event_type == "review.created":
            product_id = payload.get("product_id")
            new_rating = payload.get("new_average_rating")
            review_count = payload.get("review_count")
            if product_id and new_rating is not None:
                await svc.update_product_partial(
                    product_id,
                    {"average_rating": new_rating, "review_count": review_count or 0},
                )
                logger.info(f"Updated product '{product_id}' rating to {new_rating} ({review_count} reviews).")

        else:
            logger.debug(f"Unhandled event type: {event_type}")

    async def _route_to_dlq(self, original_topic: str, event_data: Dict[str, Any]):
        """Publish failed event to Dead-Letter Queue topic."""
        dlq_topic = f"{original_topic}.dlq"
        logger.error(f"Routing unrecoverable event to DLQ topic '{dlq_topic}'.")
        if self.dlq_producer:
            try:
                await self.dlq_producer.send_and_wait(dlq_topic, value=event_data)
                logger.info(f"Dispatched event to DLQ '{dlq_topic}'.")
            except Exception as e:
                logger.error(f"Failed to publish to DLQ topic '{dlq_topic}': {e}")


search_consumer = SearchEventConsumer()
