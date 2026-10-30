"""
FastAPI route dependencies for Cart Service.
Extracts verified user claims from JWT or guest session identifiers from headers.
"""

import uuid
from typing import Any, Dict, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)


async def get_optional_user_claims(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[Dict[str, Any]]:
    """Extract claims if valid Bearer token is provided; otherwise returns None."""
    if not credentials or not credentials.credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return None

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "CUSTOMER"),
    }


async def get_current_user_claims(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, Any]:
    """Require valid Bearer token for protected cart operations (e.g. merging)."""
    claims = await get_optional_user_claims(credentials)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or are invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


async def get_cart_identity(
    claims: Optional[Dict[str, Any]] = Depends(get_optional_user_claims),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> Dict[str, Any]:
    """
    Resolve cart ownership identity.
    Prefers user_id from token if present; falls back to session_id for guest carts.
    """
    if claims:
        return {
            "user_id": claims["user_id"],
            "session_id": x_session_id,
            "is_guest": False,
        }

    if not x_session_id:
        # Default guest session if neither auth nor session header is provided
        x_session_id = str(uuid.uuid4())

    return {
        "user_id": None,
        "session_id": x_session_id,
        "is_guest": True,
    }
