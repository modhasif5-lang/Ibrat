"""
Security utilities for User Service:
- Password hashing & verification
- JWT Access and Refresh token generation & verification
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from app.config import get_settings

settings = get_settings()

# Password hashing with passlib/bcrypt fallback
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        """Hash a plain text password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

except Exception:
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"sha256${salt}${hashed}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if hashed_password.startswith("sha256$"):
            _, salt, hashed = hashed_password.split("$")
            return hashlib.sha256((plain_password + salt).encode()).hexdigest() == hashed
        return False


# JWT Encoding & Decoding
try:
    from jose import JWTError, jwt
except ImportError:
    jwt = None
    JWTError = Exception


def create_access_token(
    subject: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": "access",
    }

    if jwt is not None:
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    # Minimal fallback token for test environments without python-jose
    import json, base64
    header_b64 = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hashlib.sha256(f"{header_b64}.{payload_b64}.{settings.JWT_SECRET}".encode()).hexdigest()
    return f"{header_b64}.{payload_b64}.{sig}"


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

        # Fallback decoder
        import json, base64
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


def generate_refresh_token() -> Tuple[str, str, datetime]:
    """
    Generate an opaque, high-entropy refresh token.
    Returns:
        (raw_token, token_hash, expires_at)
    """
    raw_token = secrets.token_urlsafe(64)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    return raw_token, token_hash, expires_at


def hash_token(token: str) -> str:
    """Hash an opaque token using SHA-256 for safe database storage."""
    return hashlib.sha256(token.encode()).hexdigest()
