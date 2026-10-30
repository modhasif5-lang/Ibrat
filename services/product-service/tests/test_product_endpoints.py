"""
Integration tests for Product Service endpoints and administrative authorization guards.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint returns status healthy and service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "product-service"


def test_ready_check_endpoint():
    """Verify readiness check reports database dependency status."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "checks" in data
    assert "database" in data["checks"]


def test_admin_routes_require_authorization():
    """Verify admin endpoints reject unauthenticated requests with 401."""
    # Create product requires admin
    resp_prod = client.post("/products", json={"name": "Test"})
    assert resp_prod.status_code == 401

    # Create category requires admin
    resp_cat = client.post("/categories", json={"name": "Test Cat"})
    assert resp_cat.status_code == 401

    # Create collection requires admin
    resp_col = client.post("/collections", json={"name": "Test Coll"})
    assert resp_col.status_code == 401


def test_review_submission_requires_authorization():
    """Verify review submission requires authenticated user token."""
    import uuid
    dummy_id = uuid.uuid4()
    resp_rev = client.post(
        f"/reviews/product/{dummy_id}",
        json={"rating": 5, "comment": "Great quality footwear."},
    )
    assert resp_rev.status_code == 401
