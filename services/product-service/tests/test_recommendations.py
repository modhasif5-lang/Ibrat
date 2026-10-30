"""
Unit and API integration tests for the dedicated Recommendation Engine.
Tests similarity scoring, explainability reasons, popularity ranking, personalized matching, and fallbacks.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.product import CustomizationOption, Product, ProductVariant
from app.schemas.recommendation import (
    PersonalizedPreferenceInput,
    RecommendationItemResponse,
    RecommendationListResponse,
)
from app.services.recommendation_engine import RecommendationEngine

client = TestClient(app)


def test_similarity_computation_matching_signals():
    """Verify footwear similarity calculation with matching category, heel height, and material."""
    cat_id = uuid.uuid4()
    p1 = Product(
        id=uuid.uuid4(),
        name="Aurelia Satin Pump",
        slug="aurelia-pump",
        category_id=cat_id,
        base_price=Decimal("380.00"),
        material="Italian Silk Satin",
        average_rating=4.9,
        review_count=12,
        customizations=[
            CustomizationOption(type="HEEL_SIZE", value="2 inch", is_available=True),
            CustomizationOption(type="HEEL_SIZE", value="3 inch", is_available=True),
        ],
        variants=[
            ProductVariant(sku="AUR-GLD-38", size="38", color_name="Champagne Gold", is_active=True)
        ],
    )

    p2 = Product(
        id=uuid.uuid4(),
        name="Camilla Satin Slingback",
        slug="camilla-slingback",
        category_id=cat_id,
        base_price=Decimal("350.00"),
        material="French Silk Satin",
        average_rating=4.8,
        review_count=8,
        customizations=[
            CustomizationOption(type="HEEL_SIZE", value="2 inch", is_available=True),
        ],
        variants=[
            ProductVariant(sku="CAM-GLD-38", size="38", color_name="Champagne Gold", is_active=True)
        ],
    )

    engine = RecommendationEngine(db=None)
    score, reason = engine.compute_similarity(p1, p2)

    assert score > 0.5
    assert "Same" in reason or "heel" in reason.lower() or "Satin" in reason


def test_similarity_computation_dissimilar_products():
    """Verify dissimilar footwear (different category, heels, and materials) receive low score."""
    p1 = Product(
        id=uuid.uuid4(),
        name="Stiletto Evening Pump",
        slug="stiletto-pump",
        category_id=uuid.uuid4(),
        base_price=Decimal("450.00"),
        material="Silk Velvet",
        customizations=[CustomizationOption(type="HEEL_SIZE", value="3 inch", is_available=True)],
        variants=[],
    )

    p2 = Product(
        id=uuid.uuid4(),
        name="Casual Leather Flat",
        slug="casual-flat",
        category_id=uuid.uuid4(),
        base_price=Decimal("150.00"),
        material="Full Grain Calf",
        customizations=[CustomizationOption(type="HEEL_SIZE", value="1 inch", is_available=True)],
        variants=[],
    )

    engine = RecommendationEngine(db=None)
    score, reason = engine.compute_similarity(p1, p2)

    assert score < 0.2


def test_personalized_preference_schema():
    """Verify personalized preference schema serialization."""
    pref = PersonalizedPreferenceInput(
        preferred_heel_sizes=["2 inch", "3 inch"],
        preferred_shoe_size="38",
    )
    assert "2 inch" in pref.preferred_heel_sizes
    assert pref.preferred_shoe_size == "38"


def test_popular_recommendations_endpoint_mocked():
    """Verify /recommendations/popular endpoint responds with valid schema."""
    sample_item = RecommendationItemResponse(
        id=uuid.uuid4(),
        name="Aurelia Pump",
        slug="aurelia-pump",
        base_price=Decimal("380.00"),
        material="Silk Satin",
        average_rating=5.0,
        review_count=14,
        is_featured=True,
        is_new_arrival=True,
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        recommendation_reason="Trending customer favorite",
        similarity_score=1.0,
    )
    mock_res = RecommendationListResponse(
        algorithm="POPULARITY",
        total=1,
        cached=False,
        items=[sample_item],
    )

    with patch.object(RecommendationEngine, "get_popular_products", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_res
        response = client.get("/recommendations/popular?limit=4")
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"] == "POPULARITY"
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Aurelia Pump"


def test_personalized_recommendations_endpoint_mocked():
    """Verify personalized endpoint handles preferences and fallback."""
    sample_item = RecommendationItemResponse(
        id=uuid.uuid4(),
        name="Valentina Velvet Mule",
        slug="valentina-velvet-mule",
        base_price=Decimal("295.00"),
        material="Silk Velvet",
        average_rating=4.8,
        review_count=6,
        is_featured=False,
        is_new_arrival=True,
        heel_sizes=["2 inch"],
        recommendation_reason="Available in your preferred 2 inch heel",
        similarity_score=0.85,
    )
    mock_res = RecommendationListResponse(
        algorithm="PERSONALIZED",
        total=1,
        cached=False,
        items=[sample_item],
    )

    with patch.object(RecommendationEngine, "get_personalized_recommendations", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_res
        response = client.get("/recommendations/personalized?heel_sizes=2 inch&limit=4")
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"] == "PERSONALIZED"
        assert len(data["items"]) == 1


def test_similar_recommendations_endpoint_mocked():
    """Verify similar products endpoint returns content-based recommendations."""
    prod_id = uuid.uuid4()
    mock_res = RecommendationListResponse(
        algorithm="CONTENT_SIMILARITY",
        total=0,
        cached=False,
        items=[],
    )

    with patch.object(RecommendationEngine, "get_similar_products", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = mock_res
        response = client.get(f"/recommendations/similar/{prod_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"] == "CONTENT_SIMILARITY"
