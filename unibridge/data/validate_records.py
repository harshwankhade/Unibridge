"""
validate_records.py
-------------------
Validates every record in processed_records.json against these rules:
  1. All required fields are present (source-specific sets)
  2. title is non-empty
  3. abstract is non-empty
  4. is_indian is exactly a Python bool (not 0/1 or None)
  5. domain is non-blank and belongs to the known vocabulary
  6. contributors is a list
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT    = os.path.join(BASE_DIR, "processed_records.json")

# ── Expected schemas ──────────────────────────────────────────────────────────
PATENT_FIELDS = {
    "id", "source", "title", "abstract", "university",
    "date", "contributors", "domain", "is_indian", "cpc_codes",
}
PAPER_FIELDS = {
    "id", "source", "title", "abstract", "university",
    "date", "contributors", "domain", "is_indian", "fields_of_study",
}

# All domain values that process_data.py can emit
VALID_DOMAINS = {
    "Life Sciences", "Mechanical Engineering", "Chemistry & Materials",
    "Textiles & Manufacturing", "Civil Engineering", "Mechanical & Thermal Engineering",
    "Physics & Computing", "Electronics & Electrical",
    "Computing & AI", "Engineering", "Mathematics",
    "Environmental Science", "Economics & Business", "Social Sciences",
    "Other",
}

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading", INPUT)
with open(INPUT, encoding="utf-8") as f:
    records = json.load(f)
print(f"Loaded {len(records):,} records\n")

# ── Validate ──────────────────────────────────────────────────────────────────
errors  = []
warnings = []

for i, r in enumerate(records):
    src = r.get("source", "?")
    rid = r.get("id", f"index_{i}")
    ref = f"[{i}] id={rid}"

    # 1. Required fields
    expected = PATENT_FIELDS if src == "patent" else PAPER_FIELDS
    missing  = expected - r.keys()
    if missing:
        errors.append(f"{ref}  MISSING FIELDS: {sorted(missing)}")

    # 2. Non-empty title
    title = r.get("title", "")
    if not isinstance(title, str) or not title.strip():
        errors.append(f"{ref}  EMPTY/NULL TITLE (got {repr(title)[:60]})")

    # 3. Non-empty abstract
    abstract = r.get("abstract", "")
    if not isinstance(abstract, str) or not abstract.strip():
        errors.append(f"{ref}  EMPTY/NULL ABSTRACT (got {repr(abstract)[:60]})")

    # 4. is_indian must be bool
    is_indian = r.get("is_indian")
    if not isinstance(is_indian, bool):
        errors.append(
            f"{ref}  is_indian is {type(is_indian).__name__} = {repr(is_indian)}, expected bool"
        )

    # 5. domain non-blank and known
    domain = r.get("domain", "")
    if not domain or not domain.strip():
        errors.append(f"{ref}  BLANK domain")
    elif domain not in VALID_DOMAINS:
        warnings.append(f"{ref}  UNEXPECTED domain: {repr(domain)}")

    # 6. contributors is a list
    contribs = r.get("contributors")
    if not isinstance(contribs, list):
        errors.append(
            f"{ref}  contributors is {type(contribs).__name__}, expected list"
        )

# ── Report ────────────────────────────────────────────────────────────────────
SEP = "=" * 58

print(SEP)
print("VALIDATION REPORT")
print(SEP)
print(f"Total records checked : {len(records):,}")
print(f"Errors found          : {len(errors)}")
print(f"Warnings found        : {len(warnings)}")
print()

if errors:
    print("--- ERRORS (first 30 shown) ---")
    for e in errors[:30]:
        print("  [ERR]", e)
    if len(errors) > 30:
        print(f"  ... and {len(errors)-30} more errors.")
else:
    print("  [OK] Zero errors.")

if warnings:
    print()
    print("--- WARNINGS ---")
    for w in warnings[:30]:
        print("  [WARN]", w)
else:
    print("  [OK] Zero warnings.")

# ── Per-field summary ─────────────────────────────────────────────────────────
total = len(records)
n_patents  = sum(1 for r in records if r.get("source") == "patent")
n_papers   = sum(1 for r in records if r.get("source") == "paper")
n_title_ok = sum(1 for r in records if isinstance(r.get("title"), str) and r["title"].strip())
n_abs_ok   = sum(1 for r in records if isinstance(r.get("abstract"), str) and r["abstract"].strip())
n_indian_t = sum(1 for r in records if r.get("is_indian") is True)
n_indian_f = sum(1 for r in records if r.get("is_indian") is False)
n_bool_ok  = sum(1 for r in records if isinstance(r.get("is_indian"), bool))
n_dom_ok   = sum(1 for r in records if r.get("domain", "").strip())
n_no_contribs = sum(1 for r in records if r.get("contributors") == [])

from collections import Counter
domain_dist = Counter(r.get("domain", "") for r in records)

print()
print("--- FIELD SUMMARY ---")
print(f"  source=patent        : {n_patents:>5,}  /  {total:,}")
print(f"  source=paper         : {n_papers:>5,}  /  {total:,}")
print(f"  title non-empty      : {n_title_ok:>5,}  /  {total:,}  {'OK' if n_title_ok==total else 'FAIL'}")
print(f"  abstract non-empty   : {n_abs_ok:>5,}  /  {total:,}  {'OK' if n_abs_ok==total else 'FAIL'}")
print(f"  is_indian is bool    : {n_bool_ok:>5,}  /  {total:,}  {'OK' if n_bool_ok==total else 'FAIL'}")
print(f"  is_indian = True     : {n_indian_t:>5,}")
print(f"  is_indian = False    : {n_indian_f:>5,}")
print(f"  domain non-blank     : {n_dom_ok:>5,}  /  {total:,}  {'OK' if n_dom_ok==total else 'FAIL'}")
print(f"  contributors = []    : {n_no_contribs:>5,}  (empty list allowed)")
print()
print("--- DOMAIN DISTRIBUTION ---")
for domain, count in sorted(domain_dist.items(), key=lambda x: -x[1]):
    pct = count / total * 100
    print(f"  {domain:<38} {count:>5}  ({pct:4.1f}%)")

print(SEP)
sys.exit(1 if errors else 0)
