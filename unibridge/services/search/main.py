"""
services/search/main.py
-----------------------
Search Service — orchestrates the full UniBridge search pipeline:

  1. Token verification   (Auth Service)
  2. Query translation    (query_translator.py → OpenAI)
  3. Vector retrieval     (retriever.py → Data Service / ChromaDB)
  4. Cross-encoder re-rank (retriever.py → sentence-transformers)
  5. Relevance explanation (explainer.py → OpenAI)
  6. Analytics logging    (Analytics Service — fire-and-forget)

Endpoints:
    POST /search   → full pipeline
    GET  /health   → liveness probe

Run:
    python main.py
    # or
    uvicorn main:app --reload --port 8002
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure sibling modules are importable regardless of CWD
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# Load .env from project root
from dotenv import load_dotenv
_ENV_PATH = _HERE.parents[1] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# ---------------------------------------------------------------------------
# Step 1 — Imports and app setup
# ---------------------------------------------------------------------------
import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from explainer import explain_results
from query_translator import translate_query
from retriever import retrieve

app = FastAPI(
    title="UniBridge Search Service",
    description="Orchestrates query translation → vector retrieval → re-ranking → explanation.",
    version="1.0.0",
)

ANALYTICS_SERVICE_URL = os.environ.get("ANALYTICS_SERVICE_URL", "http://localhost:8005")
AUTH_SERVICE_URL      = os.environ.get("AUTH_SERVICE_URL",      "http://localhost:8001")

_VALID_CATEGORIES = {"solve", "benchmark", "landscape"}


# ---------------------------------------------------------------------------
# Step 2 — Request model
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    category: str = "solve"   # "solve" | "benchmark" | "landscape"
    n_results: int = 10


# ---------------------------------------------------------------------------
# Step 3 — Token verification helper
# ---------------------------------------------------------------------------

def verify_token(authorization: str | None) -> dict:
    """
    Validate a Bearer JWT via the Auth Service and return the decoded payload.

    Raises HTTP 401 if the header is missing, malformed, or rejected.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        response = httpx.get(
            f"{AUTH_SERVICE_URL}/verify",
            headers={"Authorization": authorization},
            timeout=10.0,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return response.json()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


# ---------------------------------------------------------------------------
# Step 4 — Analytics logging helper (fire-and-forget)
# ---------------------------------------------------------------------------

def log_to_analytics(
    user_id: int | None,
    query: str,
    translated_query: str,
    category: str,
    results: list[dict],
) -> None:
    """
    POST a search event to the Analytics Service.
    Any failure is silently swallowed — analytics must never break search.
    """
    try:
        # Extract unique domains / universities (up to 3 each)
        seen_domains = []
        seen_unis    = []
        for r in results:
            d = r.get("domain", "")
            u = r.get("university", "")
            if d and d not in seen_domains:
                seen_domains.append(d)
            if u and u not in seen_unis:
                seen_unis.append(u)

        payload = {
            "user_id":          user_id,
            "query":            query,
            "translated_query": translated_query,
            "category":         category,
            "result_count":     len(results),
            "top_domains":      seen_domains[:3],
            "top_universities": seen_unis[:3],
        }

        httpx.post(
            f"{ANALYTICS_SERVICE_URL}/event",
            json=payload,
            timeout=5.0,
        )

    except Exception:   # noqa: BLE001
        pass            # analytics must never crash the search response


# ---------------------------------------------------------------------------
# Step 5 — POST /search
# ---------------------------------------------------------------------------

@app.post("/search")
def search(
    request: SearchRequest,
    authorization: str | None = Header(default=None),
):
    """
    Full search pipeline: translate → retrieve → re-rank → explain.
    Authorization header is optional (allows unauthenticated demo access).
    """
    # 1. Optional auth
    user_id: int | None = None
    if authorization:
        user_info = verify_token(authorization)
        user_id   = user_info.get("user_id")

    # 2. Validate category
    if request.category not in _VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    query    = request.query
    category = request.category

    # 3. Translate query
    translation_result  = translate_query(query, category)
    translated_query    = translation_result["translated_query"]

    # 4. Retrieve (vector search + re-rank)
    try:
        results = retrieve(translated_query, n_results=50, top_n=request.n_results)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Search service temporarily unavailable",
        ) from exc

    # 5. Explain results (use ORIGINAL query for business-facing explanations)
    try:
        results = explain_results(query, results, category)
    except Exception:   # noqa: BLE001
        # Explanations are non-critical — fall back to empty strings
        for r in results:
            r.setdefault("explanation", "")

    # 6. Log to analytics (fire-and-forget — never blocks response)
    try:
        log_to_analytics(user_id, query, translated_query, category, results)
    except Exception:   # noqa: BLE001
        pass

    # 7. Build response
    formatted_results = [
        {
            "id":            r.get("id",            ""),
            "title":         r.get("title",         ""),
            "abstract":      r.get("abstract",      ""),
            "university":    r.get("university",    ""),
            "source":        r.get("source",        ""),
            "domain":        r.get("domain",        ""),
            "date":          r.get("date",          ""),
            "contributors":  r.get("contributors",  []),
            "is_indian":     r.get("is_indian",     False),
            "trl":           r.get("trl",           None),
            "trl_confidence": r.get("trl_confidence", None),
            "trl_reasoning": r.get("trl_reasoning", ""),
            "rerank_score":  r.get("rerank_score",  None),
            "explanation":   r.get("explanation",   ""),
        }
        for r in results
    ]

    return {
        "query":            query,
        "translated_query": translated_query,
        "category":         category,
        "results":          formatted_results,
        "total_results":    len(formatted_results),
    }


# ---------------------------------------------------------------------------
# Step 6 — GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Step 7 — Run config
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
