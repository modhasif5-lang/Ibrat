"""
Kafka Domain Event Schemas for Product Service.
Defines strongly typed event payloads published for search indexing and analytics.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    """Standard envelope for all Ibrat asynchronous Kafka events."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    producer: str = "product-service"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any]


class ProductCreatedEventPayload(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    collection_id: Optional[str] = None
    collection_name: Optional[str] = None
    base_price: float
    discount_price: Optional[float] = None
    effective_price: float
    material: Optional[str] = None
    sole_material: Optional[str] = None
    heel_sizes: List[str] = []
    sizes: List[str] = []
    colors: List[str] = []
    is_active: bool = True
    is_featured: bool = False
    is_new_arrival: bool = False
    is_in_stock: bool = True
    average_rating: float = 0.0
    review_count: int = 0
    primary_image_url: Optional[str] = None


class ProductDeletedEventPayload(BaseModel):
    product_id: str


class ReviewCreatedEventPayload(BaseModel):
    review_id: str
    product_id: str
    user_id: str
    rating: int
    new_average_rating: float
    review_count: int
