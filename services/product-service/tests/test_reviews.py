"""
Unit and integration tests for Product Service Reviews, Ratings, and Moderation.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas.product import (
    RatingDistribution,
    ReviewApprovalUpdate,
    ReviewCreate,
    ReviewUpdate,
)

client = TestClient(app)


def test_review_rating_validation_bounds():
    """Verify star ratings are strictly bounded between 1 and 5."""
    # Valid star ratings
    r1 = ReviewCreate(rating=1, comment="Toe box is slightly narrow.")
    r3 = ReviewCreate(rating=3, comment="Decent comfort, elegant finish.")
    r5 = ReviewCreate(rating=5, comment="Spectacular Tuscan silk satin bridal shoe!")
    assert r1.rating == 1
    assert r3.rating == 3
    assert r5.rating == 5

    # Invalid star ratings
    with pytest.raises(ValidationError):
        ReviewCreate(rating=0, comment="Unacceptable rating")

    with pytest.raises(ValidationError):
        ReviewCreate(rating=6, comment="Above 5 stars not permitted")


def test_review_update_schema():
    """Verify partial review updates."""
    up = ReviewUpdate(rating=4, comment="Updated opinion after wearing for 6 hours.")
    assert up.rating == 4
    assert "wearing for 6 hours" in up.comment


def test_review_approval_update_schema():
    """Verify review approval status schema."""
    app_true = ReviewApprovalUpdate(is_approved=True)
    app_false = ReviewApprovalUpdate(is_approved=False)
    assert app_true.is_approved is True
    assert app_false.is_approved is False


def test_rating_distribution_calculation():
    """Verify 5-tier rating distribution counter."""
    dist = RatingDistribution(
        five_star=12,
        four_star=4,
        three_star=1,
        two_star=0,
        one_star=0,
    )
    total = dist.five_star + dist.four_star + dist.three_star + dist.two_star + dist.one_star
    assert total == 17


def test_review_endpoints_require_authentication():
    """Verify submitting reviews and uploading review images requires authentication."""
    prod_id = uuid.uuid4()
    rev_id = uuid.uuid4()

    # Submit review without token
    resp_submit = client.post(
        f"/reviews/product/{prod_id}",
        json={"rating": 5, "comment": "Great shoe"},
    )
    assert resp_submit.status_code == 401

    # Edit review without token
    resp_edit = client.put(
        f"/reviews/{rev_id}",
        json={"rating": 4, "comment": "Edited comment"},
    )
    assert resp_edit.status_code == 401

    # Delete review without token
    resp_del = client.delete(f"/reviews/{rev_id}")
    assert resp_del.status_code == 401


def test_admin_review_moderation_requires_admin_authorization():
    """Verify admin review moderation and list endpoints require admin permissions."""
    rev_id = uuid.uuid4()

    resp_list = client.get("/reviews/admin/list")
    assert resp_list.status_code == 401

    resp_mod = client.patch(
        f"/reviews/admin/{rev_id}/moderate",
        json={"is_approved": True},
    )
    assert resp_mod.status_code == 401

    resp_admin_del = client.delete(f"/reviews/admin/{rev_id}")
    assert resp_admin_del.status_code == 401
