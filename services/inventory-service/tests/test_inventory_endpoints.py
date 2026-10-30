"""
Integration tests for Inventory Service API routes and admin guards.
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
    assert data["service"] == "inventory-service"


def test_ready_check_endpoint():
    """Verify readiness check reports database dependency status."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "checks" in data
    assert "database" in data["checks"]


def test_reserve_stock_validation():
    """Verify invalid reservation requests are rejected with 422."""
    response = client.post(
        "/inventory/reserve",
        json={"variant_id": "not-a-uuid", "quantity": 0},
    )
    assert response.status_code == 422


def test_admin_routes_require_authorization():
    """Verify administrative inventory endpoints reject unauthenticated calls."""
    # List admin inventory
    resp_list = client.get("/inventory/admin/list")
    assert resp_list.status_code == 401

    # Create inventory
    resp_create = client.post("/inventory/admin", json={"sku": "TEST"})
    assert resp_create.status_code == 401

    # Cleanup expired reservations
    resp_cleanup = client.post("/inventory/admin/cleanup-expired")
    assert resp_cleanup.status_code == 401
