"""
Integration tests for Cart Service API endpoints.
Validates health, readiness, item addition validation, and authentication guards.
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
    assert data["service"] == "cart-service"


def test_ready_check_endpoint():
    """Verify readiness check reports database dependency status."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "checks" in data
    assert "database" in data["checks"]


def test_add_item_validation_error_invalid_fields():
    """Verify invalid payloads (malformed UUID, quantity 0) trigger 422."""
    response = client.post(
        "/cart/items",
        json={
            "product_id": "not-a-uuid",
            "variant_id": "not-a-uuid",
            "quantity": 0,
            "unit_price": 200.0,
        },
    )
    assert response.status_code == 422


def test_add_item_validation_error_invalid_heel():
    """Verify unauthorized heel customization is rejected with 422."""
    response = client.post(
        "/cart/items",
        json={
            "product_id": "a1000000-0000-0000-0000-000000000001",
            "variant_id": "v1000000-0000-0000-0000-000000000003",
            "quantity": 1,
            "selected_customization": "6 inch",
            "unit_price": 380.0,
        },
    )
    assert response.status_code == 422


def test_merge_cart_requires_authentication():
    """Verify merging guest carts into a user cart requires a valid Bearer token."""
    response = client.post(
        "/cart/merge",
        json={"guest_session_id": "guest-session-123"},
    )
    assert response.status_code == 401
