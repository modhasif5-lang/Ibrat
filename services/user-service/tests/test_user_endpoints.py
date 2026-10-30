"""
Integration tests for User Service API routes and security guards.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint returns status healthy and service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "user-service"
    assert "version" in data


def test_ready_check_endpoint():
    """Verify readiness check reports service dependency statuses."""
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "checks" in data
    assert "database" in data["checks"]


def test_register_invalid_payload():
    """Verify registration rejects invalid email or missing fields."""
    response = client.post(
        "/auth/register",
        json={"email": "not-valid", "password": "123"},
    )
    assert response.status_code == 422


def test_login_invalid_payload():
    """Verify login rejects invalid email payload."""
    response = client.post(
        "/auth/login",
        json={"email": "invalid-email-string", "password": ""},
    )
    assert response.status_code == 422


def test_protected_routes_require_authentication():
    """Verify protected endpoints reject unauthenticated requests with 401."""
    # /auth/me
    resp_me = client.get("/auth/me")
    assert resp_me.status_code == 401

    # /users/profile
    resp_profile = client.get("/users/profile")
    assert resp_profile.status_code == 401

    # /users/preferences
    resp_pref = client.get("/users/preferences")
    assert resp_pref.status_code == 401

    # /users/wishlist
    resp_wishlist = client.get("/users/wishlist")
    assert resp_wishlist.status_code == 401

    # /users/notifications
    resp_notif = client.get("/users/notifications")
    assert resp_notif.status_code == 401

    # /users/admin/list
    resp_admin = client.get("/users/admin/list")
    assert resp_admin.status_code == 401
