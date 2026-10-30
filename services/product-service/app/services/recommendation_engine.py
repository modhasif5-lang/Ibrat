"""
Dedicated Recommendation Engine for Ibrat Luxury Footwear.
Implements content-based footwear similarity, popularity ranking, category recommendations,
personalized user style matching, fallback guarantees, and Redis caching.
"""

import hashlib
import json
import logging
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple
from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import cache_service
from app.models.product import Category, Product
from app.repositories.product_repository import ProductRepository
from app.schemas.recommendation import (
    PersonalizedPreferenceInput,
    RecommendationItemResponse,
    RecommendationListResponse,
)

logger = logging.getLogger(__name__)

CACHE_TTL_RECOMMENDATIONS = 300  # 5 minutes


class RecommendationEngine:
    """Dedicated module providing explainable footwear recommendations with Redis caching."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    # ============================================================
    # Extraction Helpers
    # ============================================================

    @staticmethod
    def _extract_heel_sizes(prod: Product) -> List[str]:
        return [
            c.value for c in (prod.customizations or [])
            if c.type == "HEEL_SIZE" and c.is_available
        ]

    @staticmethod
    def _extract_colors(prod: Product) -> Set[str]:
        return {v.color_name.lower() for v in (prod.variants or []) if v.is_active}

    @staticmethod
    def _extract_sizes(prod: Product) -> Set[str]:
        return {str(v.size) for v in (prod.variants or []) if v.is_active}

    @staticmethod
    def _extract_primary_image(prod: Product) -> Optional[str]:
        if prod.images:
            for img in prod.images:
                if img.is_primary:
                    return img.url
            return prod.images[0].url
        return None

    def _to_recommendation_card(
        self,
        prod: Product,
        reason: str,
        score: Optional[float] = None,
    ) -> RecommendationItemResponse:
        """Convert Product entity to recommendation card."""
        return RecommendationItemResponse(
            id=prod.id,
            name=prod.name,
            slug=prod.slug,
            base_price=prod.base_price,
            discount_price=prod.discount_price,
            material=prod.material,
            average_rating=prod.average_rating,
            review_count=prod.review_count,
            is_featured=prod.is_featured,
            is_new_arrival=prod.is_new_arrival,
            primary_image_url=self._extract_primary_image(prod),
            category_name=prod.category.name if prod.category else None,
            heel_sizes=self._extract_heel_sizes(prod),
            recommendation_reason=reason,
            similarity_score=round(score, 2) if score is not None else None,
        )

    # ============================================================
    # Content-Based Similarity Scoring
    # ============================================================

    def compute_similarity(self, target: Product, candidate: Product) -> Tuple[float, str]:
        """
        Calculate explainable multi-signal similarity score between two footwear items.
        Weights:
          - Category match: 0.35
          - Heel size overlap: 0.25
          - Material keyword overlap: 0.15
          - Color overlap: 0.15
          - Price proximity: 0.10
        """
        score = 0.0
        reasons = []

        # 1. Category match (0.35)
        if target.category_id and candidate.category_id and target.category_id == candidate.category_id:
            score += 0.35
            cat_name = candidate.category.name if candidate.category else "collection"
            reasons.append(f"Same {cat_name} category")

        # 2. Heel size overlap (0.25)
        target_heels = set(self._extract_heel_sizes(target))
        candidate_heels = set(self._extract_heel_sizes(candidate))
        shared_heels = target_heels.intersection(candidate_heels)
        if shared_heels:
            ratio = len(shared_heels) / max(len(target_heels.union(candidate_heels)), 1)
            score += 0.25 * ratio
            reasons.append(f"Matching {', '.join(sorted(shared_heels))} heel height")

        # 3. Material match (0.15)
        if target.material and candidate.material:
            t_words = set(target.material.lower().split())
            c_words = set(candidate.material.lower().split())
            common_words = t_words.intersection(c_words)
            # Filter non-stop words
            meaningful = {w for w in common_words if len(w) > 3}
            if meaningful:
                score += 0.15
                reasons.append(f"Shared {' '.join(sorted(meaningful)).title()} craft")

        # 4. Color palette overlap (0.15)
        target_colors = self._extract_colors(target)
        candidate_colors = self._extract_colors(candidate)
        shared_colors = target_colors.intersection(candidate_colors)
        if shared_colors:
            score += 0.15
            reasons.append(f"Available in {' & '.join(sorted(shared_colors)).title()}")

        # 5. Price proximity (0.10)
        t_price = float(target.discount_price or target.base_price)
        c_price = float(candidate.discount_price or candidate.base_price)
        max_p = max(t_price, c_price, 1.0)
        price_diff = abs(t_price - c_price)
        proximity = max(0.0, 1.0 - (price_diff / max_p))
        score += 0.10 * proximity

        explanation = " • ".join(reasons) if reasons else "Coordinating footwear design"
        return score, explanation

    # ============================================================
    # Strategy 1: Similar Products ("You May Also Like")
    # ============================================================

    async def get_similar_products(
        self, product_id: uuid.UUID, limit: int = 6
    ) -> RecommendationListResponse:
        """Content-based recommendations for product detail page with fallback and Redis cache."""
        cache_key = f"rec:similar:{product_id}:{limit}"
        cached = await cache_service.get_json(cache_key)
        if cached:
            return RecommendationListResponse(
                algorithm="CONTENT_SIMILARITY",
                total=len(cached),
                cached=True,
                items=[RecommendationItemResponse(**i) for i in cached],
            )

        # Fetch target product
        target = await self.repo.get_product_by_id(product_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target footwear product '{product_id}' not found.",
            )

        # Fetch candidate active products
        stmt = (
            select(Product)
            .where(Product.is_active == True, Product.id != product_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.collection),
                selectinload(Product.images),
                selectinload(Product.customizations),
                selectinload(Product.variants),
            )
        )
        candidates = list((await self.db.execute(stmt)).scalars().all())

        # Score candidates
        scored_candidates: List[Tuple[float, str, Product]] = []
        for cand in candidates:
            sim_score, reason = self.compute_similarity(target, cand)
            scored_candidates.append((sim_score, reason, cand))

        # Sort descending by similarity
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        items: List[RecommendationItemResponse] = []
        used_ids: Set[uuid.UUID] = {target.id}
        for score, reason, cand in scored_candidates[:limit]:
            used_ids.add(cand.id)
            items.append(self._to_recommendation_card(cand, reason, score))

        # If candidates fewer than limit, fill with fallback popular items
        if len(items) < limit:
            fallback = await self._get_fallback_candidates(limit - len(items), exclude_ids=used_ids)
            items.extend(fallback)

        # Store in Redis
        await cache_service.set_json(
            cache_key, [i.model_dump(mode="json") for i in items], ttl_seconds=CACHE_TTL_RECOMMENDATIONS
        )

        return RecommendationListResponse(
            algorithm="CONTENT_SIMILARITY",
            total=len(items),
            cached=False,
            items=items,
        )

    # ============================================================
    # Strategy 2: Popular / Trending Footwear
    # ============================================================

    async def get_popular_products(self, limit: int = 8) -> RecommendationListResponse:
        """Top-rated, most-reviewed, and featured footwear items with Redis caching."""
        cache_key = f"rec:popular:{limit}"
        cached = await cache_service.get_json(cache_key)
        if cached:
            return RecommendationListResponse(
                algorithm="POPULARITY",
                total=len(cached),
                cached=True,
                items=[RecommendationItemResponse(**i) for i in cached],
            )

        stmt = (
            select(Product)
            .where(Product.is_active == True)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.customizations),
                selectinload(Product.variants),
            )
            .order_by(
                desc(Product.is_featured),
                desc(Product.average_rating),
                desc(Product.review_count),
            )
            .limit(limit)
        )
        products = list((await self.db.execute(stmt)).scalars().all())

        items = [
            self._to_recommendation_card(
                p,
                reason=f"Trending choice ({p.average_rating}★ from {p.review_count} reviews)",
                score=min(1.0, float(p.average_rating) / 5.0),
            )
            for p in products
        ]

        await cache_service.set_json(
            cache_key, [i.model_dump(mode="json") for i in items], ttl_seconds=CACHE_TTL_RECOMMENDATIONS
        )

        return RecommendationListResponse(
            algorithm="POPULARITY",
            total=len(items),
            cached=False,
            items=items,
        )

    # ============================================================
    # Strategy 3: Category Recommendations
    # ============================================================

    async def get_category_recommendations(
        self, category_id: uuid.UUID, limit: int = 6
    ) -> RecommendationListResponse:
        """Top recommended footwear in a specific category with fallback."""
        cache_key = f"rec:category:{category_id}:{limit}"
        cached = await cache_service.get_json(cache_key)
        if cached:
            return RecommendationListResponse(
                algorithm="CATEGORY",
                total=len(cached),
                cached=True,
                items=[RecommendationItemResponse(**i) for i in cached],
            )

        stmt = (
            select(Product)
            .where(Product.is_active == True, Product.category_id == category_id)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.customizations),
                selectinload(Product.variants),
            )
            .order_by(desc(Product.is_featured), desc(Product.average_rating))
            .limit(limit)
        )
        products = list((await self.db.execute(stmt)).scalars().all())

        items = [
            self._to_recommendation_card(
                p,
                reason=f"Top choice in {p.category.name if p.category else 'collection'}",
                score=0.9,
            )
            for p in products
        ]

        # Fallback if category has fewer products than limit
        if len(items) < limit:
            used = {p.id for p in products}
            fallback = await self._get_fallback_candidates(limit - len(items), exclude_ids=used)
            items.extend(fallback)

        await cache_service.set_json(
            cache_key, [i.model_dump(mode="json") for i in items], ttl_seconds=CACHE_TTL_RECOMMENDATIONS
        )

        return RecommendationListResponse(
            algorithm="CATEGORY",
            total=len(items),
            cached=False,
            items=items,
        )

    # ============================================================
    # Strategy 4: Personalized Recommendations
    # ============================================================

    async def get_personalized_recommendations(
        self,
        preferences: PersonalizedPreferenceInput,
        user_id: Optional[uuid.UUID] = None,
        limit: int = 8,
    ) -> RecommendationListResponse:
        """
        Personalized style recommendations based on customer preferred heel sizes, shoe size, and category.
        Falls back seamlessly to popularity ranking when customer signals are sparse.
        """
        pref_hash = hashlib.md5(
            f"{user_id}:{preferences.preferred_heel_sizes}:{preferences.preferred_shoe_size}:{preferences.favorite_category_id}".encode()
        ).hexdigest()
        cache_key = f"rec:personalized:{pref_hash}:{limit}"
        cached = await cache_service.get_json(cache_key)
        if cached:
            return RecommendationListResponse(
                algorithm="PERSONALIZED",
                total=len(cached),
                cached=True,
                items=[RecommendationItemResponse(**i) for i in cached],
            )

        # Check if preferences are sparse
        has_signals = bool(
            preferences.preferred_heel_sizes
            or preferences.preferred_shoe_size
            or preferences.favorite_category_id
        )

        if not has_signals:
            # Fallback to trending
            popular = await self.get_popular_products(limit)
            return RecommendationListResponse(
                algorithm="FALLBACK",
                total=popular.total,
                cached=popular.cached,
                items=popular.items,
            )

        # Score all active products against user preferences
        stmt = (
            select(Product)
            .where(Product.is_active == True)
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.customizations),
                selectinload(Product.variants),
            )
        )
        products = list((await self.db.execute(stmt)).scalars().all())

        scored_products: List[Tuple[float, str, Product]] = []
        preferred_heels = set(preferences.preferred_heel_sizes)

        for prod in products:
            p_score = 0.0
            reasons = []

            # 1. Heel preference match (+40)
            p_heels = set(self._extract_heel_sizes(prod))
            matched_heels = preferred_heels.intersection(p_heels)
            if matched_heels:
                p_score += 0.40
                reasons.append(f"Available in your preferred {', '.join(sorted(matched_heels))} heel")

            # 2. Shoe size preference match (+35)
            if preferences.preferred_shoe_size:
                p_sizes = self._extract_sizes(prod)
                if preferences.preferred_shoe_size in p_sizes:
                    p_score += 0.35
                    reasons.append(f"In stock in size {preferences.preferred_shoe_size}")

            # 3. Category preference match (+25)
            if preferences.favorite_category_id and prod.category_id == preferences.favorite_category_id:
                p_score += 0.25
                reasons.append("From your favorite footwear category")

            # Quality booster: ratings
            p_score += float(prod.average_rating) * 0.02

            if p_score > 0.1:
                explanation = " • ".join(reasons) if reasons else "Selected for your style profile"
                scored_products.append((p_score, explanation, prod))

        # Sort descending by score
        scored_products.sort(key=lambda x: x[0], reverse=True)

        items: List[RecommendationItemResponse] = []
        used_ids: Set[uuid.UUID] = set()
        for score, reason, prod in scored_products[:limit]:
            used_ids.add(prod.id)
            items.append(self._to_recommendation_card(prod, reason, score))

        # Fill with fallback if needed
        if len(items) < limit:
            fallback = await self._get_fallback_candidates(limit - len(items), exclude_ids=used_ids)
            items.extend(fallback)

        await cache_service.set_json(
            cache_key, [i.model_dump(mode="json") for i in items], ttl_seconds=CACHE_TTL_RECOMMENDATIONS
        )

        return RecommendationListResponse(
            algorithm="PERSONALIZED" if scored_products else "FALLBACK",
            total=len(items),
            cached=False,
            items=items,
        )

    # ============================================================
    # Fallback Guarantee Helper
    # ============================================================

    async def _get_fallback_candidates(
        self, needed_count: int, exclude_ids: Set[uuid.UUID]
    ) -> List[RecommendationItemResponse]:
        """Guarantee fallback products to eliminate empty recommendations."""
        if needed_count <= 0:
            return []

        stmt = (
            select(Product)
            .where(Product.is_active == True, Product.id.not_in(exclude_ids))
            .options(
                selectinload(Product.category),
                selectinload(Product.images),
                selectinload(Product.customizations),
                selectinload(Product.variants),
            )
            .order_by(desc(Product.average_rating), desc(Product.is_featured))
            .limit(needed_count)
        )
        fallback_products = list((await self.db.execute(stmt)).scalars().all())

        return [
            self._to_recommendation_card(
                p,
                reason="Curated luxury recommendation",
                score=0.8,
            )
            for p in fallback_products
        ]
