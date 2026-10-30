"""
Unit tests for User Service security, hashing, and token workflows.
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hashing():
    """Verify password hashing produces valid salted hashes and matches correctly."""
    pwd = "SecureFootwearPassword@123"
    hashed = hash_password(pwd)

    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword@123", hashed) is False


def test_jwt_access_token():
    """Verify access token creation, claims encoding, and decoding."""
    user_id = str(uuid.uuid4())
    email = "customer@ibrat.com"
    role = "CUSTOMER"

    token = create_access_token(
        subject=user_id,
        role=role,
        email=email,
        expires_delta=timedelta(minutes=15),
    )

    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["role"] == role
    assert payload["type"] == "access"


def test_expired_access_token():
    """Verify expired tokens are rejected by decoder."""
    user_id = str(uuid.uuid4())
    token = create_access_token(
        subject=user_id,
        role="CUSTOMER",
        email="expired@ibrat.com",
        expires_delta=timedelta(seconds=-10),  # expired in past
    )

    payload = decode_access_token(token)
    assert payload is None


def test_refresh_token_generation():
    """Verify refresh token generation and deterministic hashing."""
    raw_token, token_hash, expires_at = generate_refresh_token()

    assert len(raw_token) >= 64
    assert len(token_hash) == 64  # SHA-256 hex string length
    assert expires_at > datetime.now(timezone.utc)
    assert hash_token(raw_token) == token_hash
