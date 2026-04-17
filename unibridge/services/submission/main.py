from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import httpx
import os
from database import SessionLocal, engine
from models import Base, Submission
from jose import jwt, JWTError
# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
JWT_SECRET = os.environ.get("JWT_SECRET", "unibridge-secret-key")
JWT_ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:8003")

# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def verify_token(authorization: Optional[str]) -> dict:
    """Decode JWT locally — no auth service call needed."""
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class SubmitRequest(BaseModel):
    title: str
    abstract: str
    university: str
    contributors: str       # comma-separated names
    domain: str
    ip_type: str            # "patent" or "paper"
    legal_status: str = "PENDING"


class UpdateSubmissionRequest(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    contributors: Optional[str] = None
    domain: Optional[str] = None


class AdminActionRequest(BaseModel):
    admin_note: Optional[str] = ""

# ---------------------------------------------------------------------------
# Helper: serialize a Submission ORM object to a plain dict
# ---------------------------------------------------------------------------

def submission_to_dict(s: Submission) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "abstract": s.abstract,
        "university": s.university,
        "contributors": s.contributors,
        "domain": s.domain,
        "ip_type": s.ip_type,
        "legal_status": s.legal_status,
        "submitted_by": s.submitted_by,
        "submitted_by_email": s.submitted_by_email,
        "status": s.status,
        "admin_note": s.admin_note,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
def submit(
    request: SubmitRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)

    if request.ip_type not in ("patent", "paper"):
        raise HTTPException(status_code=400, detail="Invalid ip_type")

    submission = Submission(
        title=request.title,
        abstract=request.abstract,
        university=request.university,
        contributors=request.contributors,
        domain=request.domain,
        ip_type=request.ip_type,
        legal_status=request.legal_status,
        submitted_by=user_info["user_id"],
        submitted_by_email=user_info["email"],
        status="pending",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "message": "Submission received successfully",
        "submission_id": submission.id,
        "status": "pending",
    }


@app.get("/submissions")
def list_submissions(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)
    role = user_info.get("role")

    if role == "industry":
        raise HTTPException(status_code=403, detail="Access denied")

    if role == "university":
        submissions = (
            db.query(Submission)
            .filter(Submission.submitted_by == user_info["user_id"])
            .all()
        )
    else:  # admin
        submissions = db.query(Submission).all()

    return {
        "submissions": [submission_to_dict(s) for s in submissions],
        "total": len(submissions),
    }


@app.get("/submissions/{id}")
def get_submission(
    id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)
    role = user_info.get("role")

    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if role == "university" and submission.submitted_by != user_info["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return submission_to_dict(submission)


@app.put("/submissions/{id}")
def update_submission(
    id: int,
    request: UpdateSubmissionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)
    role = user_info.get("role")

    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if role != "university" or submission.submitted_by != user_info["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    if submission.status != "pending":
        raise HTTPException(
            status_code=400, detail="Cannot edit a submission that has been reviewed"
        )

    if request.title is not None:
        submission.title = request.title
    if request.abstract is not None:
        submission.abstract = request.abstract
    if request.contributors is not None:
        submission.contributors = request.contributors
    if request.domain is not None:
        submission.domain = request.domain

    submission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)

    return submission_to_dict(submission)


@app.post("/submissions/{id}/approve")
def approve_submission(
    id: int,
    request: AdminActionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)

    if user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status == "approved":
        raise HTTPException(status_code=400, detail="Already approved")

    submission.status = "approved"
    submission.admin_note = request.admin_note
    submission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)

    # Trigger Data Service ingestion
    ingestion_status = "success"
    payload = {
        "id": "submission_" + str(submission.id),
        "title": submission.title,
        "abstract": submission.abstract,
        "university": submission.university,
        "source": submission.ip_type,
        "domain": submission.domain,
        "date": str(submission.created_at.year),
        "contributors": submission.contributors.split(","),
        "is_indian": False,
        "legal_status": submission.legal_status,
    }

    try:
        ingest_response = httpx.post(DATA_SERVICE_URL + "/ingest", json=payload, timeout=10)
        if ingest_response.status_code != 200:
            ingestion_status = "failed"
    except Exception:
        ingestion_status = "failed"

    return {
        "message": "Submission approved and sent for indexing",
        "submission_id": submission.id,
        "ingestion_status": ingestion_status,
    }


@app.post("/submissions/{id}/reject")
def reject_submission(
    id: int,
    request: AdminActionRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    user_info = verify_token(authorization)

    if user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    submission = db.query(Submission).filter(Submission.id == id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status == "rejected":
        raise HTTPException(status_code=400, detail="Already rejected")

    submission.status = "rejected"
    submission.admin_note = request.admin_note
    submission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)

    return {
        "message": "Submission rejected",
        "submission_id": submission.id,
        "admin_note": submission.admin_note,
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
