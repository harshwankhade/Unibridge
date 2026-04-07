"""
retriever.py
------------
Two-stage retrieval pipeline for UniBridge semantic search:

  Stage 1 — Vector Search  : POST to the Data Service (/search) which uses
                             ChromaDB + sentence-transformers to find the top-N
                             semantically similar records.

  Stage 2 — Cross-Encoder  : Re-ranks the Stage-1 results using a fine-tuned
                             MS MARCO cross-encoder for more precise relevance
                             scoring, then returns the top_n results.

Usage:
    from retriever import retrieve
    results = retrieve("electrochemical battery degradation", n_results=50, top_n=10)
"""

from __future__ import annotations

import os
import sys

import httpx
from sentence_transformers import CrossEncoder

# ---------------------------------------------------------------------------
# Step 1 — Setup
# ---------------------------------------------------------------------------

DATA_SERVICE_URL = os.environ.get("DATA_URL", "http://localhost:8003")

print("Loading cross-encoder (cross-encoder/ms-marco-MiniLM-L-6-v2)...",
      flush=True)
_cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("Cross-encoder ready.", flush=True)


# ---------------------------------------------------------------------------
# Step 2 — Stage 1: Vector Search
# ---------------------------------------------------------------------------

def vector_search(query: str, n_results: int = 50) -> list[dict]:
    """
    Fetch candidate records from the Data Service using vector similarity search.

    Parameters
    ----------
    query     : translated search query
    n_results : how many candidates to retrieve (default 50)

    Returns
    -------
    list of record dicts from the Data Service /search response

    Raises
    ------
    RuntimeError if the HTTP request fails
    """
    try:
        response = httpx.post(
            f"{DATA_SERVICE_URL}/search",
            json={"query": query, "n_results": n_results},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["results"]

    except Exception as exc:
        raise RuntimeError(
            f"[vector_search] Data Service request failed: {type(exc).__name__}: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Step 3 — Stage 2: Cross-Encoder Re-ranking
# ---------------------------------------------------------------------------

def rerank(query: str, results: list[dict], top_n: int = 10) -> list[dict]:
    """
    Re-rank candidate records using a cross-encoder relevance model.

    Parameters
    ----------
    query   : query string to score against each result
    results : candidate records from vector_search
    top_n   : number of results to return after re-ranking (default 10)

    Returns
    -------
    top_n records sorted by rerank_score descending
    """
    # 1. Build (query, document) pairs for the cross-encoder
    pairs = [
        [query, f"{r.get('title', '')} {r.get('abstract', '')}"]
        for r in results
    ]

    # 2. Score all pairs in one batch
    scores = _cross_encoder.predict(pairs, show_progress_bar=False)

    # 3. Attach scores to results
    for i, result in enumerate(results):
        result["rerank_score"] = float(scores[i])

    # 4. Sort by score descending
    results.sort(key=lambda r: r["rerank_score"], reverse=True)

    # 5. Return top_n
    return results[:top_n]


# ---------------------------------------------------------------------------
# Step 4 — Master retrieval function
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    n_results: int = 50,
    top_n: int = 10,
) -> list[dict]:
    """
    Two-stage retrieval pipeline: vector search → cross-encoder re-ranking.

    Parameters
    ----------
    query     : translated query string
    n_results : number of candidates to fetch from vector search (default 50)
    top_n     : number of final results after re-ranking (default 10)

    Returns
    -------
    list of re-ranked result dicts (each has a 'rerank_score' field)
    """
    # Stage 1 — Vector search
    candidates = vector_search(query, n_results)

    # If too few candidates, skip re-ranking and return as-is
    if len(candidates) < top_n:
        return candidates

    # Stage 2 — Re-ranking
    return rerank(query, candidates, top_n)


# ---------------------------------------------------------------------------
# Step 5 — Self-test  (requires Data Service running on port 8003)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "electrochemical degradation lithium-ion battery cathode materials",
        "deep learning medical image segmentation convolutional neural networks",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        try:
            results = retrieve(query)
            print(f"Returned {len(results)} results")
            for r in results:
                score = r.get("rerank_score", 0.0)
                title = r.get("title", "")[:60]
                uni   = r.get("university", "")
                print(f"  [{score:.3f}] {title} — {uni}")
        except Exception as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)
        print()
