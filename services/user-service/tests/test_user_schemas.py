"""
Unit tests for User Service Pydantic schemas and footwear validation rules.
"""

import uuid
import pytest
from pydantic import ValidationError

from app.schemas.user import (
    AdminUserRoleUpdateRequest,
    PasswordChangeRequest,
    UserPreferenceUpdateRequest,
    UserRegisterRequest,
)


def test_user_register_schema_validation():
    """Verify password minimum length and email validation."""
    # Valid registration
    valid_req = UserRegisterRequest(
        email="shoelover@ibrat.com",
        password="ValidPassword@123",
        full_name="Elena Gilbert",
        phone="+1234567890",
    )
    assert valid_req.email == "shoelover@ibrat.com"

    # Password too short (< 8 chars)
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="shoelover@ibrat.com",
            password="short",
        )

    # Invalid email format
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="not-an-email",
            password="ValidPassword@123",
        )


def test_footwear_preference_schema():
    """Verify footwear sizing and preference fields."""
    pref = UserPreferenceUpdateRequest(
        preferred_size="39",
        preferred_heel="2 inch",
        preferred_colors="Midnight Black, Rose Gold",
        newsletter_subscribed=True,
    )
    assert pref.preferred_size == "39"
    assert pref.preferred_heel == "2 inch"


def test_admin_role_update_validation():
    """Verify admin role assignment accepts only CUSTOMER or ADMIN."""
    valid_admin = AdminUserRoleUpdateRequest(role="ADMIN")
    assert valid_admin.role == "ADMIN"

    valid_customer = AdminUserRoleUpdateRequest(role="CUSTOMER")
    assert valid_customer.role == "CUSTOMER"

    with pytest.raises(ValidationError):
        AdminUserRoleUpdateRequest(role="SUPERUSER")
