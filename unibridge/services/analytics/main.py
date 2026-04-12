from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from collections import Counter
from database import SessionLocal, engine
from models import Base, SearchEvent

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

Base.metadata.create_all(bind=engine)

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
# Request model
# ---------------------------------------------------------------------------

class EventRequest(BaseModel):
    user_id:          Optional[int]       = None
    query:            str
    translated_query: Optional[str]       = None
    category:         str
    result_count:     int                 = 0
    top_domains:      Optional[List[str]] = []
    top_universities: Optional[List[str]] = []

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split(value: Optional[str]) -> List[str]:
    """Split a comma-separated string back into a list, filtering empty strings."""
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _event_to_dict(e: SearchEvent) -> dict:
    return {
        "id":               e.id,
        "query":            e.query,
        "category":         e.category,
        "result_count":     e.result_count,
        "top_domains":      _split(e.top_domains),
        "top_universities": _split(e.top_universities),
        "created_at":       e.created_at.isoformat() if e.created_at else None,
    }

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/event")
def log_event(request: EventRequest, db: Session = Depends(get_db)):
    """Log a search event. Never raises — returns event_id=None on failure."""
    try:
        event = SearchEvent(
            user_id          = request.user_id,
            query            = request.query,
            translated_query = request.translated_query,
            category         = request.category,
            result_count     = request.result_count,
            top_domains      = ",".join(request.top_domains)      if request.top_domains      else "",
            top_universities = ",".join(request.top_universities) if request.top_universities else "",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return {"status": "logged", "event_id": event.id}
    except Exception:
        return {"status": "logged", "event_id": None}


@app.get("/trending")
def trending(limit: int = 10, db: Session = Depends(get_db)):
    """Top queries by frequency over the last 7 days."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    events = db.query(SearchEvent).filter(SearchEvent.created_at >= cutoff).all()

    if not events:
        return {"trending": [], "period": "last 7 days"}

    counts = Counter(e.query.lower().strip() for e in events)
    top = [{"query": q, "count": c} for q, c in counts.most_common(limit)]

    return {"trending": top, "period": "last 7 days"}


@app.get("/gaps")
def gaps(db: Session = Depends(get_db)):
    """Queries with zero results over the last 30 days — potential research gaps."""
    cutoff = datetime.utcnow() - timedelta(days=30)
    events = (
        db.query(SearchEvent)
        .filter(SearchEvent.created_at >= cutoff, SearchEvent.result_count == 0)
        .all()
    )

    if not events:
        return {"gaps": [], "description": "Queries with no results — potential research gaps"}

    counts = Counter(e.query.lower().strip() for e in events)
    top = [{"query": q, "count": c} for q, c in counts.most_common(10)]

    return {
        "gaps": top,
        "description": "Queries with no results — potential research gaps",
    }


@app.get("/trl-distribution")
def trl_distribution(db: Session = Depends(get_db)):
    """Category distribution across all events (used as a TRL proxy)."""
    events = db.query(SearchEvent).all()

    category_counts: dict = {}
    for e in events:
        category_counts[e.category] = category_counts.get(e.category, 0) + 1

    return {
        "trl_distribution": category_counts,
        "total_events":     len(events),
    }


@app.get("/category-breakdown")
def category_breakdown(db: Session = Depends(get_db)):
    """Frequency of each domain across all search events."""
    events = db.query(SearchEvent).all()

    all_domains: List[str] = []
    for e in events:
        all_domains.extend(_split(e.top_domains))

    counts = Counter(all_domains)
    breakdown = [
        {"domain": domain, "count": cnt}
        for domain, cnt in counts.most_common()
    ]

    return {
        "category_breakdown": breakdown,
        "total_events":       len(events),
    }


@app.get("/recent")
def recent(limit: int = 20, db: Session = Depends(get_db)):
    """Most recent search events in descending chronological order."""
    events = (
        db.query(SearchEvent)
        .order_by(SearchEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    result = [_event_to_dict(e) for e in events]
    return {"recent": result, "total_returned": len(result)}


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
