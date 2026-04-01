"""
process_data.py
---------------
Normalises raw_patents.json and raw_papers.json into a unified
processed_records.json file.

Run:
    python data/process_data.py
"""

import io
import json
import os
import sys
from collections import defaultdict

# Ensure UTF-8 output on all platforms (avoids cp1252 issues on Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATENTS = os.path.join(BASE_DIR, "raw_patents.json")
RAW_PAPERS  = os.path.join(BASE_DIR, "raw_papers.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "processed_records.json")

# ---------------------------------------------------------------------------
# University reference — used to decide is_indian
# ---------------------------------------------------------------------------
# Import directly from the sibling module so the list stays in one place.
sys.path.insert(0, BASE_DIR)
from universities import INDIAN_UNIVERSITIES

# Build a fast lookup set (lower-cased for case-insensitive comparison)
INDIAN_SET = {u.lower() for u in INDIAN_UNIVERSITIES}


def is_indian_university(name: str) -> bool:
    """Return True when *name* matches any entry in INDIAN_UNIVERSITIES."""
    return name.strip().lower() in INDIAN_SET


# ---------------------------------------------------------------------------
# Domain mappings
# ---------------------------------------------------------------------------

# CPC section letter -> domain  (use only first character of first code)
CPC_DOMAIN_MAP = {
    "A": "Life Sciences",
    "B": "Mechanical Engineering",
    "C": "Chemistry & Materials",
    "D": "Textiles & Manufacturing",
    "E": "Civil Engineering",
    "F": "Mechanical & Thermal Engineering",
    "G": "Physics & Computing",
    "H": "Electronics & Electrical",
}

# Field of study -> domain
FOS_DOMAIN_MAP = {
    "Computer Science":       "Computing & AI",
    "Medicine":               "Life Sciences",
    "Biology":                "Life Sciences",
    "Chemistry":              "Chemistry & Materials",
    "Physics":                "Physics & Computing",
    "Engineering":            "Engineering",
    "Mathematics":            "Mathematics",
    "Environmental Science":  "Environmental Science",
    "Economics":              "Economics & Business",
    "Psychology":             "Social Sciences",
}


def map_cpc_domain(cpc_codes: list) -> str:
    """Return domain string from the first CPC code, or 'Other'."""
    if not cpc_codes:
        return "Other"
    first_code = str(cpc_codes[0]).strip()
    if first_code:
        section = first_code[0].upper()
        return CPC_DOMAIN_MAP.get(section, "Other")
    return "Other"


def map_fos_domain(fields: list) -> str:
    """Return domain string from the first recognised field of study, or 'Other'."""
    if not fields:
        return "Other"
    for field in fields:
        domain = FOS_DOMAIN_MAP.get(str(field).strip())
        if domain:
            return domain
    return "Other"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_str(value, default: str = "") -> str:
    """Return a stripped string; falls back to *default* for None/non-string."""
    if value is None:
        return default
    return str(value).strip()


def safe_list(value) -> list:
    """Return *value* as a list, or an empty list if None / not iterable."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def normalise_patent(record: dict, index: int) -> dict | None:
    """
    Normalise a raw patent record.
    Returns None when the record should be skipped (missing title/abstract).
    """
    title    = safe_str(record.get("title"))
    abstract = safe_str(record.get("abstract"))

    # Skip records with empty title or abstract
    if not title or not abstract:
        return None

    university  = safe_str(record.get("university"))
    date        = safe_str(record.get("date"))
    cpc_codes   = safe_list(record.get("cpc_codes"))
    inventors   = safe_list(record.get("inventors"))
    contributors = [safe_str(name) for name in inventors if safe_str(name)]

    return {
        "id":           f"patent_{index}",
        "source":       "patent",
        "title":        title,
        "abstract":     abstract,
        "university":   university,
        "date":         date,
        "contributors": contributors,
        "domain":       map_cpc_domain(cpc_codes),
        "is_indian":    is_indian_university(university),
        "cpc_codes":    cpc_codes,
    }


def normalise_paper(record: dict, index: int) -> dict | None:
    """
    Normalise a raw paper record.
    Returns None when the record should be skipped (missing title/abstract).
    """
    title    = safe_str(record.get("title"))
    abstract = safe_str(record.get("abstract"))

    # Skip records with empty title or abstract
    if not title or not abstract:
        return None

    university     = safe_str(record.get("university"))
    year           = record.get("year")
    date           = str(year).strip() if year is not None else ""
    fields         = safe_list(record.get("fields_of_study"))
    authors        = safe_list(record.get("authors"))
    contributors   = [safe_str(name) for name in authors if safe_str(name)]

    return {
        "id":              f"paper_{index}",
        "source":          "paper",
        "title":           title,
        "abstract":        abstract,
        "university":      university,
        "date":            date,
        "contributors":    contributors,
        "domain":          map_fos_domain(fields),
        "is_indian":       is_indian_university(university),
        "fields_of_study": fields,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UniBridge — Data Processing Pipeline")
    print("=" * 60)

    # ── Load raw data ──────────────────────────────────────────────
    print(f"\n[1/4] Loading raw patents from  {RAW_PATENTS}")
    with open(RAW_PATENTS, encoding="utf-8") as f:
        raw_patents = json.load(f)

    print(f"[1/4] Loading raw papers from   {RAW_PAPERS}")
    with open(RAW_PAPERS, encoding="utf-8") as f:
        raw_papers = json.load(f)

    print(f"      Raw patents: {len(raw_patents):,}  |  Raw papers: {len(raw_papers):,}")

    # ── Process patents ────────────────────────────────────────────
    print("\n[2/4] Normalising patents …")
    processed_patents = []
    skipped_patents   = 0

    for i, rec in enumerate(raw_patents):
        normalised = normalise_patent(rec, i)
        if normalised is None:
            skipped_patents += 1
        else:
            processed_patents.append(normalised)

    print(f"      Kept: {len(processed_patents):,}  |  Skipped: {skipped_patents:,}")

    # ── Process papers ─────────────────────────────────────────────
    print("\n[3/4] Normalising papers …")
    processed_papers = []
    skipped_papers   = 0

    for i, rec in enumerate(raw_papers):
        normalised = normalise_paper(rec, i)
        if normalised is None:
            skipped_papers += 1
        else:
            processed_papers.append(normalised)

    print(f"      Kept: {len(processed_papers):,}  |  Skipped: {skipped_papers:,}")

    # ── Merge & save ───────────────────────────────────────────────
    all_records = processed_patents + processed_papers

    print(f"\n[4/4] Saving {len(all_records):,} records -> {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print("      Done.")

    # ── Summary ────────────────────────────────────────────────────
    total_skipped = skipped_patents + skipped_papers
    indian_count  = sum(1 for r in all_records if r["is_indian"])

    domain_dist: dict[str, int] = defaultdict(int)
    for r in all_records:
        domain_dist[r["domain"]] += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total records   : {len(all_records):,}")
    print(f"  Patents          : {len(processed_patents):,}")
    print(f"  Papers           : {len(processed_papers):,}")
    print(f"  Indian records   : {indian_count:,}")
    print(f"  Records skipped  : {total_skipped:,}  "
          f"(patents: {skipped_patents}, papers: {skipped_papers})")
    print("\n  Domain distribution:")
    for domain, count in sorted(domain_dist.items(), key=lambda x: -x[1]):
        bar = "█" * (count * 40 // max(domain_dist.values()))
        print(f"    {domain:<35} {count:>5}  {bar}")
    print("=" * 60)


if __name__ == "__main__":
    main()
