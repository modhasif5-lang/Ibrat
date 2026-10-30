"""
Recommendation Engine API Routes.
Exposes similar footwear, trending popular styles, category picks, and personalized recommendations.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_user_claims
from app.schemas.recommendation import (
    PersonalizedPreferenceInput,
    RecommendationListResponse,
)
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "/similar/{product_id}",
    response_model=RecommendationListResponse,
    summary="Content-based similar footwear ('You may also like')",
)
async def get_similar_footwear(
    product_id: uuid.UUID,
    limit: int = Query(6, ge=1, le=20, description="Max recommended items to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes multi-signal footwear similarity based on category, heel height options,
    materials, and colorways with fallback guarantees and Redis caching.
    """
    engine = RecommendationEngine(db)
    return await engine.get_similar_products(product_id=product_id, limit=limit)


@router.get(
    "/popular",
    response_model=RecommendationListResponse,
    summary="Trending and top-rated footwear",
)
async def get_popular_footwear(
    limit: int = Query(8, ge=1, le=20, description="Max trending items to return"),
    db: AsyncSession = Depends(get_db),
):
    """Returns top-rated, featured, and most-reviewed luxury footwear styles."""
    engine = RecommendationEngine(db)
    return await engine.get_popular_products(limit=limit)


@router.get(
    "/category/{category_id}",
    response_model=RecommendationListResponse,
    summary="Top recommended footwear in a specific category",
)
async def get_category_recommendations(
    category_id: uuid.UUID,
    limit: int = Query(6, ge=1, le=20, description="Max category items to return"),
    db: AsyncSession = Depends(get_db),
):
    """Top-rated footwear picks within a category with fallback."""
    engine = RecommendationEngine(db)
    return await engine.get_category_recommendations(category_id=category_id, limit=limit)


@router.get(
    "/personalized",
    response_model=RecommendationListResponse,
    summary="Personalized footwear styles based on customer preferences",
)
async def get_personalized_footwear(
    heel_sizes: Optional[List[str]] = Query(None, description="Preferred heel heights ('1 inch', '2 inch', '3 inch')"),
    shoe_size: Optional[str] = Query(None, description="Preferred shoe size ('36'-'41')"),
    category_id: Optional[uuid.UUID] = Query(None, description="Favorite footwear category"),
    limit: int = Query(8, ge=1, le=20, description="Max personalized items to return"),
    user_claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
    db: AsyncSession = Depends(get_db),
):
    """
    Personalized recommendations matching the customer's heel preference, size, and style.
    Falls back gracefully to trending footwear when preferences are not yet established.
    """
    engine = RecommendationEngine(db)
    preferences = PersonalizedPreferenceInput(
        preferred_heel_sizes=heel_sizes or [],
        preferred_shoe_size=shoe_size,
        favorite_category_id=category_id,
    )
    user_id = user_claims["user_id"] if user_claims else None
    return await engine.get_personalized_recommendations(
        preferences=preferences,
        user_id=user_id,
        limit=limit,
    )
