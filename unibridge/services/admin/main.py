from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE_URL       = os.environ.get("AUTH_URL",       "http://localhost:8001")
SUBMISSION_SERVICE_URL = os.environ.get("SUBMISSION_URL", "http://localhost:8004")
ANALYTICS_SERVICE_URL  = os.environ.get("ANALYTICS_URL",  "http://localhost:8005")
DATA_SERVICE_URL       = os.environ.get("DATA_URL",       "http://localhost:8003")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def verify_admin(authorization: Optional[str]) -> dict:
    """Verify the Bearer token and assert the caller has the admin role."""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        resp = httpx.get(
            AUTH_SERVICE_URL + "/verify",
            headers={"Authorization": authorization},
            timeout=10,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user = resp.json()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class UpdateRoleRequest(BaseModel):
    role: str


class AdminActionRequest(BaseModel):
    admin_note: Optional[str] = ""

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# User management (proxy → Auth Service)
# ---------------------------------------------------------------------------

@app.get("/users")
def list_users(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        resp = httpx.get(
            AUTH_SERVICE_URL + "/users",
            headers={"Authorization": authorization},
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Auth service unavailable")


@app.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    authorization: Optional[str] = Header(None),
):
    verify_admin(authorization)
    try:
        resp = httpx.put(
            AUTH_SERVICE_URL + f"/users/{user_id}/role",
            headers={"Authorization": authorization},
            json=request.model_dump(),
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Auth service unavailable")


@app.delete("/users/{user_id}")
def delete_user(user_id: int, authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        resp = httpx.delete(
            AUTH_SERVICE_URL + f"/users/{user_id}",
            headers={"Authorization": authorization},
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Auth service unavailable")

# ---------------------------------------------------------------------------
# Submission management (proxy → Submission Service)
# ---------------------------------------------------------------------------

@app.get("/submissions")
def list_submissions(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        resp = httpx.get(
            SUBMISSION_SERVICE_URL + "/submissions",
            headers={"Authorization": authorization},
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Submission service unavailable")


@app.get("/submissions/{submission_id}")
def get_submission(submission_id: int, authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        resp = httpx.get(
            SUBMISSION_SERVICE_URL + f"/submissions/{submission_id}",
            headers={"Authorization": authorization},
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Submission service unavailable")


@app.post("/submissions/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    request: AdminActionRequest,
    authorization: Optional[str] = Header(None),
):
    verify_admin(authorization)
    try:
        resp = httpx.post(
            SUBMISSION_SERVICE_URL + f"/submissions/{submission_id}/approve",
            headers={"Authorization": authorization},
            json=request.model_dump(),
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Submission service unavailable")


@app.post("/submissions/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    request: AdminActionRequest,
    authorization: Optional[str] = Header(None),
):
    verify_admin(authorization)
    try:
        resp = httpx.post(
            SUBMISSION_SERVICE_URL + f"/submissions/{submission_id}/reject",
            headers={"Authorization": authorization},
            json=request.model_dump(),
            timeout=10,
        )
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Submission service unavailable")

# ---------------------------------------------------------------------------
# Analytics (proxy → Analytics Service)
# ---------------------------------------------------------------------------

@app.get("/analytics/trending")
def analytics_trending(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(ANALYTICS_SERVICE_URL + "/trending", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Analytics service unavailable")


@app.get("/analytics/gaps")
def analytics_gaps(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(ANALYTICS_SERVICE_URL + "/gaps", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Analytics service unavailable")


@app.get("/analytics/trl-distribution")
def analytics_trl(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(ANALYTICS_SERVICE_URL + "/trl-distribution", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Analytics service unavailable")


@app.get("/analytics/category-breakdown")
def analytics_category(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(ANALYTICS_SERVICE_URL + "/category-breakdown", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Analytics service unavailable")


@app.get("/analytics/recent")
def analytics_recent(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(ANALYTICS_SERVICE_URL + "/recent", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Analytics service unavailable")

# ---------------------------------------------------------------------------
# Data stats (proxy → Data Service)
# ---------------------------------------------------------------------------

@app.get("/data/stats")
def data_stats(authorization: Optional[str] = Header(None)):
    verify_admin(authorization)
    try:
        return httpx.get(DATA_SERVICE_URL + "/stats", timeout=10).json()
    except Exception:
        raise HTTPException(status_code=502, detail="Data service unavailable")

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
