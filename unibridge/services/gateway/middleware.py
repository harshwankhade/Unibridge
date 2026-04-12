from jose import jwt, JWTError
from fastapi import HTTPException
import os

JWT_SECRET    = os.environ.get("JWT_SECRET", "unibridge-secret-key")
JWT_ALGORITHM = "HS256"


def verify_token(authorization: str | None) -> dict:
    """Decode and validate a Bearer JWT. Returns the payload dict."""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def check_role(payload: dict, required_roles: list) -> bool:
    """Assert the token's role is in the allowed list."""
    if payload.get("role") not in required_roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: insufficient permissions",
        )
    return True
