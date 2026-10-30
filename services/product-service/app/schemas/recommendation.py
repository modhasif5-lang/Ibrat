"""
Pydantic schemas for Recommendation Engine.
Covers similar products, trending items, personalized recommendations, and explainability reasons.
"""

import uuid
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationItemResponse(BaseModel):
    """Recommended footwear card with explainable match reason and score."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    base_price: Decimal
    discount_price: Optional[Decimal] = None
    material: Optional[str] = None
    average_rating: float
    review_count: int
    is_featured: bool
    is_new_arrival: bool
    primary_image_url: Optional[str] = None
    category_name: Optional[str] = None
    heel_sizes: List[str] = []
    recommendation_reason: str = Field(..., description="Explainable reason why this shoe was recommended")
    similarity_score: Optional[float] = Field(None, description="Calculated similarity confidence (0.0 - 1.0)")


class RecommendationListResponse(BaseModel):
    """Response envelope for recommendation queries."""
    algorithm: str = Field(..., description="Active strategy: CONTENT_SIMILARITY, POPULARITY, PERSONALIZED, or FALLBACK")
    total: int
    cached: bool = Field(False, description="Whether result was served from Redis cache")
    items: List[RecommendationItemResponse]


class PersonalizedPreferenceInput(BaseModel):
    """Customer style signals for computing personalized recommendations."""
    preferred_heel_sizes: List[str] = []   # e.g. ["1 inch", "2 inch", "3 inch"]
    preferred_shoe_size: Optional[str] = None  # e.g. "38"
    favorite_category_id: Optional[uuid.UUID] = None
