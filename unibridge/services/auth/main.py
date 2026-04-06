"""
services/auth/main.py
---------------------
Auth Service — user registration, login, JWT verification, and role management.

Endpoints:
    POST /register          → create a new user account
    POST /login             → authenticate and receive a JWT
    GET  /verify            → validate a JWT and return its payload
    GET  /users             → list all users (admin only)
    PUT  /users/{id}/role   → change a user's role (admin only)
    DELETE /users/{id}      → delete a user (admin only)
    GET  /health            → liveness probe

Run locally:
    python main.py
    # or
    uvicorn main:app --reload --port 8001
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
import bcrypt as _bcrypt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="UniBridge Auth Service",
    description="JWT-based authentication and role management.",
    version="1.0.0",
)

# Allow browser requests from any origin (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Security configuration
# ---------------------------------------------------------------------------

_SECRET_KEY = os.environ.get("JWT_SECRET", "unibridge-secret-key")
ALGORITHM   = "HS256"
EXPIRY_HRS  = 48

VALID_ROLES = {"industry", "university", "admin"}

# ---------------------------------------------------------------------------
# Database dependency
# ---------------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=EXPIRY_HRS)
    return jwt.encode(payload, _SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def _require_auth(authorization: str | None) -> dict:
    """
    Parse the Authorization header and return the decoded JWT payload.
    Raises HTTP 401 if the header is missing or the token is invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    return decode_token(parts[1])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str   # "industry" | "university" | "admin"


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateRoleRequest(BaseModel):
    role: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/register", status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Validate role
    if request.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check duplicate email
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message":  "User registered successfully",
        "user_id":  user.id,
        "email":    user.email,
        "role":     user.role,
    }


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT."""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "user_id": user.id,
        "email":   user.email,
        "role":    user.role,
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user.role,
        "user_id":      user.id,
        "email":        user.email,
    }


@app.get("/verify")
def verify(authorization: str | None = Header(default=None)):
    """Validate a Bearer JWT and return its decoded payload."""
    payload = _require_auth(authorization)
    return {
        "user_id": payload.get("user_id"),
        "email":   payload.get("email"),
        "role":    payload.get("role"),
    }


@app.get("/users")
def list_users(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Return all users. Admin access only."""
    payload = _require_auth(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    users = db.query(User).all()
    return {
        "users": [
            {
                "id":         u.id,
                "email":      u.email,
                "role":       u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
    }


@app.put("/users/{user_id}/role")
def update_role(
    user_id: int,
    request: UpdateRoleRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Change a user's role. Admin access only."""
    payload = _require_auth(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if request.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = request.role
    db.commit()

    return {
        "message":  "Role updated",
        "user_id":  user_id,
        "new_role": request.role,
    }


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Delete a user. Admin access only."""
    payload = _require_auth(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted", "user_id": user_id}


# ---------------------------------------------------------------------------
# Run config
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
