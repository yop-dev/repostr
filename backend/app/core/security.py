from typing import Any, Optional
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from .config import settings
import jwt
from jwt import PyJWKClient, InvalidTokenError


class UserPrincipal(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    claims: dict[str, Any] = {}


def _get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    return parts[1]


_jwks_client: Optional[PyJWKClient] = None

def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        if not settings.CLERK_JWKS_URL:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CLERK_JWKS_URL not configured")
        _jwks_client = PyJWKClient(settings.CLERK_JWKS_URL)
    return _jwks_client


def verify_and_decode_jwt(token: str) -> dict[str, Any]:
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token).key
        options = {"require": ["exp", "iat"], "verify_aud": bool(settings.CLERK_AUDIENCE)}
        decoded = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE if settings.CLERK_AUDIENCE else None,
            options=options,
            issuer=settings.CLERK_ISSUER if settings.CLERK_ISSUER else None,
        )
        return decoded  # type: ignore
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")


def get_current_user(authorization: Optional[str] = Header(default=None)) -> UserPrincipal:
    token = _get_bearer_token(authorization)
    claims = verify_and_decode_jwt(token)
    user_id = str(claims.get("sub"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing sub")
    email = claims.get("email")
    name = claims.get("name") or claims.get("first_name")
    return UserPrincipal(user_id=user_id, email=email, name=name, claims=claims)


def admin_required(user: UserPrincipal = Depends(get_current_user)) -> UserPrincipal:
    if not settings.ADMIN_USER_IDS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin not configured")
    admin_ids = {x.strip() for x in settings.ADMIN_USER_IDS.split(",") if x.strip()}
    if user.user_id not in admin_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

