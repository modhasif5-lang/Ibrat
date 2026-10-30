"""
Kafka Event Producer for Inventory Service.
Dispatches inventory stock change and low-stock alert events to Kafka topics.
"""

import json
import logging
from typing import Optional
from aiokafka import AIOKafkaProducer

from app.config import get_settings
from app.schemas.events import DomainEvent

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaEventProducer:
    """Asynchronous Kafka producer for inventory domain events."""

    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self._connected: bool = False

    async def start(self):
        """Initialize producer and connect to Kafka bootstrap servers."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                request_timeout_ms=5000,
            )
            await self.producer.start()
            self._connected = True
            logger.info("Inventory Service Kafka producer connected successfully.")
        except Exception as e:
            self._connected = False
            logger.warning(f"Kafka producer connection deferred (broker offline): {e}")

    async def stop(self):
        """Gracefully flush and close producer connection."""
        if self.producer and self._connected:
            await self.producer.stop()
            self._connected = False
            logger.info("Inventory Service Kafka producer stopped.")

    async def publish(self, topic: str, event: DomainEvent, key: Optional[str] = None) -> bool:
        """Publish domain event to specified Kafka topic."""
        if not self._connected or not self.producer:
            logger.debug(f"Kafka producer offline; skipping publish of {event.event_type} to {topic}.")
            return False

        try:
            event_data = event.model_dump(mode="json")
            await self.producer.send_and_wait(topic, value=event_data, key=key)
            logger.info(f"Published event {event.event_type} [id: {event.event_id}] to {topic}.")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type} to {topic}: {e}")
            return False


event_producer = KafkaEventProducer()
