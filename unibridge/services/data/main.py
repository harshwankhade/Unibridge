"""
services/data/main.py
---------------------
Data Service — manages the ChromaDB vector store and exposes REST endpoints
for semantic search, single-record ingestion, and dataset statistics.

Endpoints:
    GET  /health   → liveness probe
    POST /search   → semantic search over unibridge_records
    POST /ingest   → add a single record (with TRL prediction + embedding)
    GET  /stats    → aggregate stats over the full collection

Run locally:
    python main.py
    # or
    uvicorn main:app --reload --port 8003
"""

from __future__ import annotations

import io
import json
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Windows-safe UTF-8 stdout
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Ensure trl_classifier is importable regardless of CWD
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ---------------------------------------------------------------------------
# Step 1 — Imports and app setup
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import chromadb
from sentence_transformers import SentenceTransformer
from trl_classifier import predict_trl

app = FastAPI(
    title="UniBridge Data Service",
    description="Manages ChromaDB and exposes search, ingest, and stats endpoints.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Shared resources (loaded once at startup)
# ---------------------------------------------------------------------------
print("Loading embedding model (all-MiniLM-L6-v2)...")
_embed_model = SentenceTransformer("all-MiniLM-L6-v2")

_chroma_path   = str(_HERE / "chroma_db")
_chroma_client = chromadb.PersistentClient(path=_chroma_path)
_collection    = _chroma_client.get_or_create_collection(
    name="unibridge_records",
    metadata={"hnsw:space": "cosine"},
)

print(f"ChromaDB ready -> {_chroma_path}  ({_collection.count()} docs)")


# ---------------------------------------------------------------------------
# Step 2 — Request / response models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    n_results: int = 10


class IngestRequest(BaseModel):
    id: str
    title: str
    abstract: str
    university: str
    source: str
    domain: str
    date: str = ""
    contributors: list = []
    is_indian: bool = False
    legal_status: str = None


# ---------------------------------------------------------------------------
# Step 3 — GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Step 4 — POST /search
# ---------------------------------------------------------------------------

@app.post("/search")
def search(request: SearchRequest):
    """
    Semantic search over the ChromaDB collection.

    Returns the top *n_results* records ranked by cosine similarity to the
    query embedding.
    """
    try:
        query_embedding = _embed_model.encode(
            request.query, show_progress_bar=False
        ).tolist()

        n = min(request.n_results, _collection.count())
        if n == 0:
            return {"results": [], "total_returned": 0}

        raw = _collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["metadatas", "documents"],
        )

        metadatas = raw["metadatas"][0]
        ids       = raw["ids"][0]

        results = []
        for doc_id, meta in zip(ids, metadatas):
            results.append({
                "id":            doc_id,
                "title":         meta.get("title", ""),
                "abstract":      meta.get("abstract", ""),
                "university":    meta.get("university", ""),
                "source":        meta.get("source", ""),
                "domain":        meta.get("domain", ""),
                "date":          meta.get("date", ""),
                "contributors":  json.loads(meta.get("contributors", "[]")),
                "is_indian":     meta.get("is_indian") == "True",
                "trl":           meta.get("trl"),
                "trl_confidence": meta.get("trl_confidence"),
                "trl_method":    meta.get("trl_method", ""),
                "trl_reasoning": meta.get("trl_reasoning", ""),
            })

        return {"results": results, "total_returned": len(results)}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Step 5 — POST /ingest
# ---------------------------------------------------------------------------

@app.post("/ingest")
def ingest(request: IngestRequest):
    """
    Predict TRL, embed, and upsert a single record into ChromaDB.
    """
    try:
        # 1. Predict TRL
        trl_result = predict_trl(
            abstract=request.abstract,
            date_published=request.date or None,
            legal_status=request.legal_status,
        )

        # 2. Embed
        embed_text = f"{request.title} {request.abstract}"
        embedding  = _embed_model.encode(
            embed_text, show_progress_bar=False
        ).tolist()

        # 3. Build metadata (ChromaDB: str | int | float only)
        metadata = {
            "title":          request.title,
            "abstract":       request.abstract[:1000],
            "university":     request.university,
            "source":         request.source,
            "domain":         request.domain,
            "date":           request.date,
            "contributors":   json.dumps(request.contributors),
            "is_indian":      str(request.is_indian),
            "trl":            int(trl_result["trl"]),
            "trl_confidence": float(trl_result["confidence"]),
            "trl_method":     str(trl_result["method"]),
            "trl_reasoning":  str(trl_result.get("reasoning", "")),
        }

        # 4. Upsert into ChromaDB
        _collection.upsert(
            ids=[request.id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[embed_text],
        )

        # 5. Return confirmation
        return {
            "status":     "ingested",
            "id":         request.id,
            "trl":        trl_result["trl"],
            "trl_method": trl_result["method"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Step 6 — GET /stats
# ---------------------------------------------------------------------------

@app.get("/stats")
def stats():
    """
    Aggregate statistics over the full ChromaDB collection.
    """
    total = _collection.count()

    if total == 0:
        return {
            "total_records":       0,
            "domain_distribution": {},
            "trl_distribution":    {},
            "source_distribution": {},
            "indian_records":      0,
        }

    try:
        all_data  = _collection.get(include=["metadatas"])
        metadatas = all_data["metadatas"]

        domain_counter  = Counter(m.get("domain", "Unknown") for m in metadatas)
        trl_counter     = Counter(str(m.get("trl", "?"))      for m in metadatas)
        source_counter  = Counter(m.get("source", "unknown")  for m in metadatas)
        indian_records  = sum(1 for m in metadatas if m.get("is_indian") == "True")

        return {
            "total_records":       total,
            "domain_distribution": dict(domain_counter),
            "trl_distribution":    dict(trl_counter),
            "source_distribution": dict(source_counter),
            "indian_records":      indian_records,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Step 7 — Run config
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
