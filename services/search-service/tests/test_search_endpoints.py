"""
Integration and API tests for Search Service endpoints.
Tests health, readiness, search queries, filter parameter validation, and autocomplete.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns status healthy and service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "search-service"


def test_readiness_endpoint():
    """Verify readiness endpoint returns dependency checks."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "elasticsearch" in data["checks"]


def test_search_endpoint_basic():
    """Verify search endpoint responds with valid SearchResultResponse structure."""
    response = client.get("/search?q=satin")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "facets" in data
    assert isinstance(data["items"], list)
    assert "categories" in data["facets"]
    assert "heel_sizes" in data["facets"]


def test_search_filters_and_sorting():
    """Verify search endpoint accepts footwear attribute filters and sorting."""
    response = client.get(
        "/search",
        params={
            "q": "pump",
            "category": "Bridal & Evening",
            "heel_size": "2 inch",
            "size": "38",
            "min_price": 100.0,
            "max_price": 500.0,
            "sort_by": "price_asc",
            "page": 1,
            "page_size": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10


def test_search_validation_errors():
    """Verify search endpoint rejects invalid sort options and negative prices."""
    # Invalid sort_by option
    resp_invalid_sort = client.get("/search?sort_by=unsupported_sort")
    assert resp_invalid_sort.status_code == 422

    # Negative price filter
    resp_negative_price = client.get("/search?min_price=-50")
    assert resp_negative_price.status_code == 422


def test_autocomplete_endpoint():
    """Verify autocomplete suggestions endpoint."""
    response = client.get("/search/autocomplete?q=Aurelia&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Aurelia"
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


def test_autocomplete_missing_query():
    """Verify autocomplete endpoint requires query string."""
    response = client.get("/search/autocomplete")
    assert response.status_code == 422
