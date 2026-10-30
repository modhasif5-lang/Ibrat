"""
Event schemas consumed by Search Service from Kafka.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class ConsumedDomainEvent(BaseModel):
    """Event wrapper received from Kafka topics."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    producer: str
    timestamp: datetime
    payload: Dict[str, Any]
