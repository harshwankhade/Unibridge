"""
ingest.py
---------
Loads processed_records.json, predicts TRL for each record using the hybrid
classifier, generates sentence embeddings, and stores everything in a
persistent ChromaDB collection for downstream semantic search.

Usage:
    python services/data/ingest.py
    # — or from this directory —
    python ingest.py
"""

from __future__ import annotations

import io
import json
import sys

# Ensure UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure trl_classifier is importable when running from any CWD
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ---------------------------------------------------------------------------
# Step 1 — Imports
# ---------------------------------------------------------------------------
import chromadb
from sentence_transformers import SentenceTransformer
from trl_classifier import predict_trl

# ---------------------------------------------------------------------------
# Step 2 — Embedding model + ChromaDB client
# ---------------------------------------------------------------------------
print("Loading embedding model (all-MiniLM-L6-v2)…")
_EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

_CHROMA_DIR = str(_HERE / "chroma_db")
_chroma_client     = chromadb.PersistentClient(path=_CHROMA_DIR)
_collection        = _chroma_client.get_or_create_collection(
    name="unibridge_records",
    metadata={"hnsw:space": "cosine"},   # cosine similarity for semantic search
)

print(f"ChromaDB initialised -> path: {_CHROMA_DIR}")
print(f"Collection 'unibridge_records' ready "
      f"(existing docs: {_collection.count()})\n")


# ---------------------------------------------------------------------------
# Step 3 — ingest_records
# ---------------------------------------------------------------------------

def ingest_records(filepath: str) -> None:
    """
    Load records from *filepath*, predict TRL, embed, and upsert into ChromaDB.

    Parameters
    ----------
    filepath : path to processed_records.json (absolute or relative to CWD)
    """
    fpath = Path(filepath)
    if not fpath.is_absolute():
        # Resolve relative paths against this file's location so the script
        # works regardless of where it is invoked from.
        fpath = (_HERE / filepath).resolve()

    print(f"Loading records from {fpath}")
    with open(fpath, encoding="utf-8") as f:
        records = json.load(f)

    total   = len(records)
    skipped = 0
    batch_ids, batch_embeddings, batch_metadatas, batch_documents = [], [], [], []

    BATCH_SIZE = 64  # upsert in chunks to keep memory under control

    def _flush(batch_ids, batch_embeddings, batch_metadatas, batch_documents):
        if batch_ids:
            _collection.upsert(
                ids=batch_ids,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                documents=batch_documents,
            )

    ingested = 0
    for i, record in enumerate(records):
        # a. Skip if abstract is missing or empty
        abstract = record.get("abstract", "").strip()
        if not abstract:
            skipped += 1
            continue

        title = record.get("title", "").strip()

        # b. Predict TRL
        trl_result = predict_trl(
            abstract=abstract,
            date_published=record.get("date"),
            legal_status=record.get("legal_status", None),
        )

        # c. Text to embed
        embed_text = f"{title} {abstract}"

        # d. Generate embedding
        embedding = _EMBED_MODEL.encode(embed_text, show_progress_bar=False).tolist()

        # e. Build metadata (ChromaDB: str | int | float only)
        metadata = {
            "title":          title,
            "abstract":       abstract[:1000],   # ChromaDB metadata has a size cap; truncate safely
            "university":     str(record.get("university", "")),
            "source":         str(record.get("source", "")),
            "domain":         str(record.get("domain", "")),
            "date":           str(record.get("date", "")),
            "contributors":   json.dumps(record.get("contributors", [])),
            "is_indian":      str(record.get("is_indian", False)),
            "trl":            int(trl_result["trl"]),
            "trl_confidence": float(trl_result["confidence"]),
            "trl_method":     str(trl_result["method"]),
            "trl_reasoning":  str(trl_result.get("reasoning", "")),
        }

        # f. Queue for upsert
        batch_ids.append(record["id"])
        batch_embeddings.append(embedding)
        batch_metadatas.append(metadata)
        batch_documents.append(embed_text)

        ingested += 1

        # Flush every BATCH_SIZE records
        if len(batch_ids) >= BATCH_SIZE:
            _flush(batch_ids, batch_embeddings, batch_metadatas, batch_documents)
            batch_ids, batch_embeddings, batch_metadatas, batch_documents = [], [], [], []

        # Progress report every 50 ingested records
        if ingested % 50 == 0:
            print(f"  Ingested {ingested}/{total}…")

    # Flush remainder
    _flush(batch_ids, batch_embeddings, batch_metadatas, batch_documents)

    print(f"\nIngestion complete.  Total records: {ingested}  |  Skipped: {skipped}")
    print(f"ChromaDB collection now contains {_collection.count()} documents.")


# ---------------------------------------------------------------------------
# Step 4 — verify_ingestion
# ---------------------------------------------------------------------------

def verify_ingestion() -> None:
    """
    Run 3 semantic test queries against the ChromaDB collection and print
    the top-3 results for each.
    """
    test_queries = [
        "machine learning for drug discovery",
        "solar energy efficiency improvement",
        "natural language processing text classification",
    ]

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 60)

        query_embedding = _EMBED_MODEL.encode(query, show_progress_bar=False).tolist()

        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, _collection.count()),
            include=["metadatas", "distances"],
        )

        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for rank, (meta, dist) in enumerate(zip(metadatas, distances), start=1):
            similarity = round(1 - dist, 3)   # cosine distance → similarity
            print(
                f"  [{rank}] {meta.get('title', '')[:60]}\n"
                f"       University : {meta.get('university', '')}\n"
                f"       Source     : {meta.get('source', '')}  |  "
                f"Domain: {meta.get('domain', '')}  |  "
                f"TRL: {meta.get('trl', '?')}  |  "
                f"Similarity: {similarity}"
            )


# ---------------------------------------------------------------------------
# Step 5 — Main block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ingest_records("../../data/processed_records.json")
    print()
    print("--- Running verification queries ---")
    verify_ingestion()
