"""
Unit tests for Search Service Pydantic schemas.
Validates footwear product documents, facet aggregations, and autocomplete structures.
"""

from datetime import datetime
import pytest
from pydantic import ValidationError

from app.schemas.search import (
    AutocompleteResponse,
    AutocompleteSuggestion,
    FacetBucket,
    PriceStatsFacet,
    ProductDocument,
    SearchFacets,
    SearchResultResponse,
)


def test_product_document_schema_valid():
    """Verify valid product document creation with footwear attributes."""
    doc = ProductDocument(
        id="prod-001",
        name="Aurelia Satin Pump",
        slug="aurelia-satin-pump",
        description="Handcrafted Italian silk satin stiletto with pointed toe.",
        category_id="cat-001",
        category_name="Bridal & Evening",
        collection_id="col-001",
        collection_name="Bridal Couture Edit",
        base_price=380.0,
        discount_price=340.0,
        effective_price=340.0,
        material="Italian Silk Satin",
        sole_material="Hand-finished Leather",
        heel_sizes=["1 inch", "2 inch", "3 inch"],
        sizes=["36", "37", "38", "39", "40"],
        colors=["Champagne Gold", "Pearl White"],
        is_active=True,
        is_featured=True,
        is_new_arrival=True,
        is_in_stock=True,
        average_rating=4.8,
        review_count=14,
        primary_image_url="/media/products/aurelia-pump-gold-1.webp",
        created_at=datetime.utcnow(),
    )

    assert doc.id == "prod-001"
    assert doc.effective_price == 340.0
    assert "2 inch" in doc.heel_sizes
    assert "38" in doc.sizes
    assert doc.is_in_stock is True


def test_product_document_defaults():
    """Verify default values for optional/boolean product attributes."""
    doc = ProductDocument(
        id="prod-002",
        name="Minimal Mule",
        slug="minimal-mule",
        description="Daily slide mule.",
        base_price=180.0,
        effective_price=180.0,
    )

    assert doc.is_active is True
    assert doc.is_featured is False
    assert doc.is_new_arrival is False
    assert doc.is_in_stock is True
    assert doc.average_rating == 0.0
    assert doc.review_count == 0
    assert doc.heel_sizes == []
    assert doc.sizes == []
    assert doc.colors == []


def test_product_document_missing_required():
    """Verify ValidationError when mandatory fields are omitted."""
    with pytest.raises(ValidationError):
        ProductDocument(
            name="Missing ID and Prices",
            description="Incomplete product",
        )


def test_search_facets_and_result_response():
    """Verify facet bucket aggregations and full search response schema."""
    facets = SearchFacets(
        categories=[FacetBucket(key="Bridal & Evening", count=5)],
        collections=[FacetBucket(key="Bridal Couture Edit", count=3)],
        heel_sizes=[
            FacetBucket(key="1 inch", count=4),
            FacetBucket(key="2 inch", count=5),
            FacetBucket(key="3 inch", count=5),
        ],
        colors=[FacetBucket(key="Champagne Gold", count=2)],
        sizes=[FacetBucket(key="38", count=5)],
        price_stats=PriceStatsFacet(min=180.0, max=450.0, avg=320.0),
    )

    doc = ProductDocument(
        id="prod-003",
        name="Seraphina Block Heel",
        slug="seraphina-block-heel",
        description="Velvet block heel sandal.",
        base_price=260.0,
        effective_price=260.0,
    )

    response = SearchResultResponse(
        total=1,
        page=1,
        size=20,
        items=[doc],
        facets=facets,
    )

    assert response.total == 1
    assert len(response.items) == 1
    assert response.facets.price_stats.min == 180.0
    assert len(response.facets.heel_sizes) == 3


def test_autocomplete_schemas():
    """Verify autocomplete suggestion and response serialization."""
    sug = AutocompleteSuggestion(
        id="prod-001",
        name="Aurelia Satin Pump",
        slug="aurelia-satin-pump",
        category_name="Bridal & Evening",
        effective_price=340.0,
        primary_image_url="/media/products/aurelia.webp",
    )
    res = AutocompleteResponse(query="Aur", suggestions=[sug])

    assert res.query == "Aur"
    assert len(res.suggestions) == 1
    assert res.suggestions[0].name == "Aurelia Satin Pump"
