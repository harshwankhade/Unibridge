"""
scrape_papers.py
----------------
Fetches academic papers from the Semantic Scholar API for universities
in the QS_UNIVERSITIES and INDIAN_UNIVERSITIES lists.

Each university name is used as a search query. The top papers with
abstracts are collected and saved to data/raw_papers.json.

API docs : https://api.semanticscholar.org/graph/v1
No API key required for basic use (100 req / 5 min rate limit).
Optional: set SEMANTIC_SCHOLAR_API_KEY in .env for higher limits.

Usage:
    python data/scrape_papers.py
"""

import json
import time
import sys
import os
import requests

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from universities import QS_UNIVERSITIES, INDIAN_UNIVERSITIES

# ---------------------------------------------------------------------------
# Load optional API key from .env
# ---------------------------------------------------------------------------
def load_env_value(key_name: str) -> str:
    value = os.environ.get(key_name, "")
    if value:
        return value
    search_dir = SCRIPT_DIR
    for _ in range(5):
        env_path = os.path.join(search_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key_name}="):
                        val = line.split("=", 1)[1].strip()
                        if val and "your_" not in val:
                            return val
        search_dir = os.path.dirname(search_dir)
    return ""


API_KEY = load_env_value("SEMANTIC_SCHOLAR_API_KEY")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_URL       = "https://api.semanticscholar.org/graph/v1/paper/search"
PER_PAGE      = 100          # papers per university (API max is 100)
DELAY_SECONDS = 1.0          # delay between requests (rate limit: ~1 req/sec)
OUTPUT_FILE   = os.path.join(SCRIPT_DIR, "raw_papers.json")

# Fields to request from Semantic Scholar
FIELDS = "title,abstract,authors,year,fieldsOfStudy"

ALL_UNIVERSITIES = INDIAN_UNIVERSITIES + QS_UNIVERSITIES

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_headers() -> dict:
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    return headers


def fetch_papers(university_name: str) -> list[dict]:
    """
    Query Semantic Scholar for papers related to this university.
    Returns a list of clean paper dicts.
    """
    params = {
        "query":  university_name,
        "fields": FIELDS,
        "limit":  PER_PAGE,
        "offset": 0,
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=get_headers(),
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print(f"  TIMEOUT")
        return []
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response else "?"
        print(f"  HTTP {code}: {exc}")
        return []
    except requests.exceptions.RequestException as exc:
        print(f"  ERROR: {exc}")
        return []
    except json.JSONDecodeError:
        print(f"  BAD JSON response")
        return []

    raw_papers = data.get("data") or []
    results = []

    for paper in raw_papers:
        if not paper:
            continue

        title    = (paper.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()

        # Skip papers without abstracts — not useful for RAG
        if not abstract:
            continue

        year = paper.get("year")

        # Extract author names
        authors = []
        for author in (paper.get("authors") or []):
            if isinstance(author, dict):
                name = (author.get("name") or "").strip()
                if name:
                    authors.append(name)

        # Fields of study — flat list of strings
        fields_of_study = []
        raw_fields = paper.get("fieldsOfStudy") or []
        for field in raw_fields:
            if isinstance(field, str) and field.strip():
                fields_of_study.append(field.strip())

        # Country tag
        country = "India" if university_name in INDIAN_UNIVERSITIES else "Global"

        results.append({
            "title":           title,
            "abstract":        abstract,
            "authors":         authors,
            "university":      university_name,
            "country":         country,
            "year":            year,
            "fields_of_study": fields_of_study,
        })

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def scrape():
    total_unis  = len(ALL_UNIVERSITIES)
    all_papers  = []
    skipped     = 0
    failed      = 0

    print(f"\n{'='*65}")
    print(f"  UniBridge — Research Paper Scraper  (Semantic Scholar)")
    print(f"  Universities : {total_unis}  |  Max per university : {PER_PAGE}")
    print(f"  API key      : {'✓ loaded' if API_KEY else '✗ not set (using public rate limit)'}")
    print(f"{'='*65}\n")

    for idx, university in enumerate(ALL_UNIVERSITIES, start=1):
        prefix = f"[{idx:>3}/{total_unis}]"

        papers = fetch_papers(university)
        count  = len(papers)

        if count == 0:
            print(f"{prefix} SKIP  (0 with abstract) — {university}")
            skipped += 1
        else:
            all_papers.extend(papers)
            print(f"{prefix} OK  {count:>3} papers — {university}")

        time.sleep(DELAY_SECONDS)

    # -----------------------------------------------------------------------
    # Save output
    # -----------------------------------------------------------------------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_papers, f, ensure_ascii=False, indent=2)

    # Summary stats
    indian_count = sum(1 for p in all_papers if p.get("country") == "India")
    global_count = len(all_papers) - indian_count

    field_counts: dict = {}
    for p in all_papers:
        for f in (p.get("fields_of_study") or []):
            field_counts[f] = field_counts.get(f, 0) + 1
    top_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    uni_counts: dict = {}
    for p in all_papers:
        uni_counts[p["university"]] = uni_counts.get(p["university"], 0) + 1
    top_unis = sorted(uni_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    print(f"\n{'='*65}")
    print(f"  Done.")
    print(f"  Total papers saved   : {len(all_papers)}")
    print(f"    Indian universities : {indian_count}")
    print(f"    Global universities : {global_count}")
    print(f"  Skipped (no abstract): {skipped}")
    print(f"\n  Top 10 universities by paper count:")
    for uni, count in top_unis:
        print(f"    {count:>4}  {uni}")
    print(f"\n  Top 10 fields of study:")
    for field, count in top_fields:
        print(f"    {count:>4}  {field}")
    print(f"\n  Output: {OUTPUT_FILE}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    scrape()
