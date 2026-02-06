"""
Authentication utilities for Supabase JWT verification.
"""

import os
from functools import lru_cache
from typing import Optional

import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, jwk
from jose.utils import base64url_decode

from config import settings

logger = structlog.get_logger(__name__)


def get_jwt_secret() -> str:
    """Get JWT secret from settings or environment with fallback."""
    secret = (
        settings.supabase_jwt_secret
        or os.environ.get("SUPABASE_JWT_SECRET", "")
        or os.environ.get("SUPABASE_JWT_SECRET ", "")  # Railway trailing space bug
    )
    return secret


def get_supabase_url() -> str:
    """Get Supabase URL from settings or environment."""
    return (
        settings.supabase_url
        or os.environ.get("SUPABASE_URL", "")
        or os.environ.get("SUPABASE_URL ", "")
    )


@lru_cache(maxsize=1)
def fetch_jwks() -> dict:
    """Fetch JWKS from Supabase for ES256 token verification."""
    supabase_url = get_supabase_url()
    if not supabase_url:
        return {}

    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    try:
        response = httpx.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning("jwks_fetch_failed", error=str(e), url=jwks_url)
        return {}

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_public_key_for_token(token: str) -> Optional[str]:
    """Get the public key for ES256 token verification from JWKS."""
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        jwks = fetch_jwks()
        keys = jwks.get("keys", [])

        for key in keys:
            if key.get("kid") == kid:
                # Convert JWK to PEM format
                return jwk.construct(key).to_pem().decode("utf-8")

        # If no matching kid, try the first key
        if keys:
            return jwk.construct(keys[0]).to_pem().decode("utf-8")

    except Exception as e:
        logger.warning("public_key_extraction_failed", error=str(e))

    return None


def decode_supabase_jwt(token: str) -> dict:
    """
    Decode and verify a Supabase JWT.

    Supports both HS256 (symmetric) and ES256 (asymmetric) algorithms.

    Returns:
        Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        # Check the algorithm used in the token
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "ES256":
            # Use public key from JWKS for ES256
            public_key = get_public_key_for_token(token)
            if not public_key:
                logger.error("es256_public_key_not_found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not verify token signature",
                )

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["ES256"],
                audience="authenticated",
            )
        else:
            # Use JWT secret for HS256
            jwt_secret = get_jwt_secret()
            if not jwt_secret:
                logger.error("jwt_secret_not_configured")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Server authentication not configured",
                )

            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )

        return payload

    except JWTError as e:
        error_str = str(e)
        logger.warning("jwt_verification_failed", error=error_str)

        # Log debug info
        try:
            header = jwt.get_unverified_header(token)
            unverified = jwt.get_unverified_claims(token)
            logger.warning(
                "jwt_debug_info",
                token_alg=header.get("alg"),
                token_aud=unverified.get("aud"),
                token_iss=unverified.get("iss"),
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency that extracts and verifies user_id from JWT.

    Usage:
        @app.post("/api/discovery/start")
        async def start(user_id: str = Depends(get_current_user_id)):
            ...
    """
    payload = decode_supabase_jwt(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
        )
    return user_id


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[str]:
    """
    Optional auth dependency -- returns None if no token provided.
    Used for endpoints that work both authenticated and anonymous.
    """
    if credentials is None:
        return None
    try:
        payload = decode_supabase_jwt(credentials.credentials)
        return payload.get("sub")
    except HTTPException:
        return None
