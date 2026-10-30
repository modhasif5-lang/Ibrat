"""
Security utilities for Product Service.
Decodes and validates JWT tokens issued by User Service.
"""

import hashlib
import json
import base64
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.config import get_settings

settings = get_settings()

try:
    from jose import JWTError, jwt
except ImportError:
    jwt = None
    JWTError = Exception


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        if jwt is not None:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            if payload.get("type") != "access":
                return None
            return payload

        # Fallback decoder for test environments without python-jose
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig = parts
        expected_sig = hashlib.sha256(f"{header_b64}.{payload_b64}.{settings.JWT_SECRET}".encode()).hexdigest()
        if sig != expected_sig:
            return None
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding).decode())
        if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
            return None
        return payload
    except Exception:
        return None
