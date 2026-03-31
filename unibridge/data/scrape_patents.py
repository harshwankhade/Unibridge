"""
scrape_patents.py
-----------------
Fetches granted patents from the Lens.org Patent API using scroll pagination.

Strategy:
  - Broad search: applicant names containing university-type keywords (phrase match)
  - Date range: 2015-2024, patent type: GRANTED_PATENT
  - Local filter: only keep patents whose applicant matches a name
    from QS_UNIVERSITIES or INDIAN_UNIVERSITIES in universities.py
  - Cap: MAX_PER_UNIVERSITY patents per university to ensure diversity
  - Incremental write: each page is flushed to disk immediately — no MemoryError
  - Target: 1000 patents saved to raw_patents.json

API docs : https://docs.api.lens.org/patent.html
Auth     : Bearer token via LENS_API_TOKEN in root .env

Usage:
    python data/scrape_patents.py
"""

import json
import time
import sys
import os
import requests

# ---------------------------------------------------------------------------
# Path setup — allow running from project root or data/ directory
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from universities import QS_UNIVERSITIES, INDIAN_UNIVERSITIES

# ---------------------------------------------------------------------------
# Load LENS_API_TOKEN from environment or root .env file
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
                        return line.split("=", 1)[1].strip()
        search_dir = os.path.dirname(search_dir)
    return ""


API_TOKEN = load_env_value("LENS_API_TOKEN")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_URL            = "https://api.lens.org/patent/search"
SCROLL_TTL         = "5m"   # scroll context TTL — 5m to safely cover 7s sleeps
PAGE_SIZE          = 100    # patents per scroll page
TARGET_PATENTS     = 1000   # stop after this many valid patents
MAX_PER_UNIVERSITY = 30     # cap per university — prevents one uni dominating
OUTPUT_FILE        = os.path.join(SCRIPT_DIR, "raw_patents.json")

# ---------------------------------------------------------------------------
# University lookup
# ---------------------------------------------------------------------------
ALL_KNOWN_UNIVERSITIES = QS_UNIVERSITIES + INDIAN_UNIVERSITIES
_UNI_CANONICAL = {u.lower(): u for u in ALL_KNOWN_UNIVERSITIES}


def match_university(applicant_name: str) -> str | None:
    """
    Returns the canonical university name if applicant_name matches
    any entry in our known university lists, else None.

    Matching rules (in order):
      1. Exact match (case-insensitive)
      2. Our university name is a substring of the applicant name
      3. Applicant name is a substring of our university name
    """
    name_lower = applicant_name.lower().strip()

    if name_lower in _UNI_CANONICAL:
        return _UNI_CANONICAL[name_lower]

    for uni_lower, uni_canonical in _UNI_CANONICAL.items():
        if uni_lower in name_lower or name_lower in uni_lower:
            return uni_canonical

    return None


# ---------------------------------------------------------------------------
# Initial search payload
# ---------------------------------------------------------------------------
def build_initial_payload() -> dict:
    """
    Broad search: GRANTED_PATENT, university-type applicants (phrase match), 2015-2024.
    The `scroll` key starts a scroll session for pagination.
    """
    return {
        "query": {
            "bool": {
                "must": [
                    # Granted patents only
                    {"term": {"publication_type": "GRANTED_PATENT"}},
                    # Date range 2010-2024
                    {
                        "range": {
                            "year_published": {"gte": 2010, "lte": 2024}
                        }
                    },
                    # Exact university name match — 50 top research universities
                    {
                        "bool": {
                            "should": [
                                {"match_phrase": {"applicant.name": "Massachusetts Institute of Technology"}},
                                {"match_phrase": {"applicant.name": "Stanford University"}},
                                {"match_phrase": {"applicant.name": "Carnegie Mellon University"}},
                                {"match_phrase": {"applicant.name": "Indian Institute of Technology"}},
                                {"match_phrase": {"applicant.name": "Indian Institute of Science"}},
                                {"match_phrase": {"applicant.name": "University of Cambridge"}},
                                {"match_phrase": {"applicant.name": "ETH Zurich"}},
                                {"match_phrase": {"applicant.name": "University of Michigan"}},
                                {"match_phrase": {"applicant.name": "Georgia Institute of Technology"}},
                                {"match_phrase": {"applicant.name": "University of Toronto"}},
                                {"match_phrase": {"applicant.name": "Johns Hopkins University"}},
                                {"match_phrase": {"applicant.name": "University of California"}},
                                {"match_phrase": {"applicant.name": "Imperial College London"}},
                                {"match_phrase": {"applicant.name": "National University of Singapore"}},
                                {"match_phrase": {"applicant.name": "University of Oxford"}},
                                {"match_phrase": {"applicant.name": "Delft University of Technology"}},
                                {"match_phrase": {"applicant.name": "Technical University of Munich"}},
                                {"match_phrase": {"applicant.name": "Korea Advanced Institute of Science and Technology"}},
                                {"match_phrase": {"applicant.name": "University of Tokyo"}},
                                {"match_phrase": {"applicant.name": "Peking University"}},
                                {"match_phrase": {"applicant.name": "Tsinghua University"}},
                                {"match_phrase": {"applicant.name": "University of Melbourne"}},
                                {"match_phrase": {"applicant.name": "University of Edinburgh"}},
                                {"match_phrase": {"applicant.name": "McGill University"}},
                                {"match_phrase": {"applicant.name": "University of Waterloo"}},
                                {"match_phrase": {"applicant.name": "Nanyang Technological University"}},
                                {"match_phrase": {"applicant.name": "Seoul National University"}},
                                {"match_phrase": {"applicant.name": "University of British Columbia"}},
                                {"match_phrase": {"applicant.name": "Ecole Polytechnique"}},
                                {"match_phrase": {"applicant.name": "KTH Royal Institute of Technology"}},
                                {"match_phrase": {"applicant.name": "Eindhoven University of Technology"}},
                                {"match_phrase": {"applicant.name": "University of New South Wales"}},
                                {"match_phrase": {"applicant.name": "Pohang University"}},
                                {"match_phrase": {"applicant.name": "Hebrew University"}},
                                {"match_phrase": {"applicant.name": "Technion"}},
                                {"match_phrase": {"applicant.name": "University of Illinois"}},
                                {"match_phrase": {"applicant.name": "University of Wisconsin"}},
                                {"match_phrase": {"applicant.name": "University of Minnesota"}},
                                {"match_phrase": {"applicant.name": "Purdue University"}},
                                {"match_phrase": {"applicant.name": "Penn State University"}},
                                {"match_phrase": {"applicant.name": "University of Texas"}},
                                {"match_phrase": {"applicant.name": "Ohio State University"}},
                                {"match_phrase": {"applicant.name": "University of Washington"}},
                                {"match_phrase": {"applicant.name": "University of Pittsburgh"}},
                                {"match_phrase": {"applicant.name": "Rutgers University"}},
                                {"match_phrase": {"applicant.name": "Boston University"}},
                                {"match_phrase": {"applicant.name": "Northeastern University"}},
                                {"match_phrase": {"applicant.name": "University of Southern California"}},
                                {"match_phrase": {"applicant.name": "New York University"}},
                                {"match_phrase": {"applicant.name": "Columbia University"}},
                                {"match_phrase": {"applicant.name": "University College Dublin"}},
                                {"match_phrase": {"applicant.name": "University of Copenhagen"}},
                                {"match_phrase": {"applicant.name": "Karlsruhe Institute of Technology"}},
                                {"match_phrase": {"applicant.name": "University of Technology Sydney"}},
                                {"match_phrase": {"applicant.name": "Hanyang University"}},
                                {"match_phrase": {"applicant.name": "University of the Witwatersrand"}},
                            ],
                            "minimum_should_match": 1
                        }
                    }
                ]
            }
        },
        # Fields to return — biblio contains all nested fields automatically
        "include": [
            "lens_id",
            "date_published",
            "publication_type",
            "abstract",
            "biblio",
        ],
        "size":   PAGE_SIZE,
        "scroll": SCROLL_TTL,
    }


def build_scroll_payload(scroll_id: str) -> dict:
    """Subsequent scroll pages — only need the scroll_id."""
    return {
        "scroll_id": scroll_id,
        "scroll":    SCROLL_TTL,
    }


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type":  "application/json",
    }


# ---------------------------------------------------------------------------
# Patent field extractors
# ---------------------------------------------------------------------------
def extract_patent(raw: dict) -> dict | None:
    """
    Transform a single raw Lens.org patent into our clean schema.
    Returns None if abstract is missing or no applicant matches our list.
    """
    biblio = raw.get("biblio") or {}

    # --- Title ---
    titles = biblio.get("invention_title") or []
    title = next(
        (t["text"] for t in titles if isinstance(t, dict) and t.get("lang") == "en"),
        titles[0]["text"] if titles and isinstance(titles[0], dict) else ""
    ).strip()

    # --- Abstract ---
    abstracts = raw.get("abstract") or []
    abstract = next(
        (a["text"] for a in abstracts if isinstance(a, dict) and a.get("lang") == "en"),
        abstracts[0]["text"] if abstracts and isinstance(abstracts[0], dict) else ""
    ).strip()
    if not abstract:
        return None  # no abstract -> not useful for RAG

    # --- Date (top-level field) ---
    date = (raw.get("date_published") or "").strip()

    # --- Inventors — extracted_name.value is the correct path ---
    inventors = []
    parties = biblio.get("parties") or {}
    for inv in (parties.get("inventors") or []):
        if isinstance(inv, dict):
            name = inv.get("extracted_name", {}).get("value", "").strip()
            if name:
                inventors.append(name)

    # --- Applicants + university matching ---
    applicant_names = []
    for app in (parties.get("applicants") or []):
        if isinstance(app, dict):
            org = app.get("extracted_name", {}).get("value", "").strip()
            if org:
                applicant_names.append(org)

    # Find first applicant that matches our university list
    matched_university = None
    for name in applicant_names:
        match = match_university(name)
        if match:
            matched_university = match
            break

    if not matched_university:
        return None  # doesn't match any known university -> skip

    # --- CPC codes — nested inside biblio ---
    cpc_codes = []
    cpc_data = biblio.get("classifications_cpc") or {}
    for cpc in (cpc_data.get("classifications") or []):
        if isinstance(cpc, dict):
            symbol = (cpc.get("symbol") or "").strip()
            if not symbol:
                continue
            # Extract group prefix: "G06N" from "G06N3/08"
            group = symbol.split("/")[0] if "/" in symbol else symbol
            if group and group not in cpc_codes:
                cpc_codes.append(group)

    # --- Country tag ---
    country = "India" if matched_university in INDIAN_UNIVERSITIES else "Global"

    return {
        "lens_id":    raw.get("lens_id", ""),
        "title":      title,
        "abstract":   abstract,
        "inventors":  inventors,
        "university": matched_university,
        "country":    country,
        "date":       date,
        "cpc_codes":  cpc_codes,
    }


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------
def scrape():
    if not API_TOKEN:
        print("\n⚠️  ERROR: No LENS_API_TOKEN found.")
        print("   Get a free token at: https://www.lens.org/lens/user/subscriptions")
        print("   Then add to your .env:  LENS_API_TOKEN=your_token_here")
        return

    headers           = get_headers()
    page_num          = 0
    scroll_id         = None
    total_seen        = 0
    total_kept        = 0
    indian_count      = 0
    global_count      = 0
    university_counts: dict = {}  # per-university counts for cap + summary
    first_record      = True      # JSON comma handling

    print(f"\n{'='*65}")
    print(f"  UniBridge — Patent Scraper  (Lens.org Scroll API)")
    print(f"  Target  : {TARGET_PATENTS} patents  |  Page size: {PAGE_SIZE}")
    print(f"  Cap     : {MAX_PER_UNIVERSITY} patents max per university")
    print(f"  Filter  : {len(ALL_KNOWN_UNIVERSITIES)} known universities")
    print(f"  Delay   : 7s between pages  (rate limit: 10 req/min)")
    print(f"  Output  : {OUTPUT_FILE}  (incremental write)")
    print(f"{'='*65}\n")

    # Open output file and write the opening bracket BEFORE the loop.
    # The finally block guarantees it is always closed with "]" even on crash.
    out_f = open(OUTPUT_FILE, "w", encoding="utf-8")
    out_f.write("[\n")

    try:
        while total_kept < TARGET_PATENTS:
            # Build payload
            if scroll_id is None:
                payload = build_initial_payload()
            else:
                payload = build_scroll_payload(scroll_id)

            # Make request
            try:
                response = requests.post(
                    API_URL,
                    json=payload,
                    headers=headers,
                    timeout=30,
                )
            except requests.exceptions.RequestException as exc:
                print(f"\n  No more results — connection error: {exc}")
                break

            # Non-200 response — treat as end of results
            if response.status_code != 200:
                print(f"\n  No more results — HTTP {response.status_code}")
                break

            # Empty body — treat as end of results
            if not response.content.strip():
                print(f"\n  No more results — empty response body")
                break

            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"\n  No more results — could not decode JSON response")
                break

            # Extract scroll_id for next page
            scroll_id = data.get("scroll_id")

            # Get results
            results = data.get("data") or []
            page_num += 1

            if not results:
                print(f"\n  No more results on page {page_num}. Done.")
                break

            # Process each patent on this page — write kept ones directly to disk
            page_kept = 0
            for raw in results:
                total_seen += 1
                patent = extract_patent(raw)
                if patent:
                    uni = patent["university"]

                    # Enforce per-university cap
                    if university_counts.get(uni, 0) >= MAX_PER_UNIVERSITY:
                        continue
                    university_counts[uni] = university_counts.get(uni, 0) + 1

                    # Track stats inline — no in-memory list needed
                    if patent["country"] == "India":
                        indian_count += 1
                    else:
                        global_count += 1

                    # Write directly to disk with correct JSON comma placement
                    record_json = json.dumps(patent, ensure_ascii=False)
                    if first_record:
                        out_f.write("  " + record_json)
                        first_record = False
                    else:
                        out_f.write(",\n  " + record_json)
                    out_f.flush()  # ensure page's data survives a crash

                    total_kept += 1
                    page_kept  += 1

                # Progress print every 100 records kept
                if total_kept > 0 and total_kept % 100 == 0 and page_kept > 0:
                    print(f"  [{total_kept:>4} kept / {total_seen:>5} seen]  "
                          f"page {page_num}  —  "
                          f"{len(university_counts)} universities covered")

                if total_kept >= TARGET_PATENTS:
                    break

            print(f"  Page {page_num:>3}  |  kept {page_kept:>3}/{len(results)}  "
                  f"|  total {total_kept}/{total_seen}  "
                  f"|  unis so far: {len(university_counts)}")

            # If no scroll_id returned, results are exhausted
            if not scroll_id:
                print("  No scroll_id returned — end of results.")
                break

            # Rate limit: 10 requests/min on trial tier -> sleep 7s between pages
            time.sleep(7)

    finally:
        # Always close the JSON array cleanly — even on crash or Ctrl+C
        out_f.write("\n]")
        out_f.close()

    # -----------------------------------------------------------------------
    # Summary — stats tracked inline above, no need to re-scan the file
    # -----------------------------------------------------------------------
    top_unis = sorted(university_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    print(f"\n{'='*65}")
    print(f"  Done.")
    print(f"  Total patents saved  : {total_kept}")
    print(f"    Indian universities : {indian_count}")
    print(f"    Global universities : {global_count}")
    print(f"  Universities covered : {len(university_counts)}")
    print(f"  Total records seen   : {total_seen}")
    print(f"  Match rate           : {total_kept/max(total_seen, 1)*100:.1f}%")
    print(f"\n  Top 10 universities by patent count:")
    for uni, count in top_unis:
        print(f"    {count:>4}  {uni}")
    print(f"\n  Output: {OUTPUT_FILE}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    scrape()
