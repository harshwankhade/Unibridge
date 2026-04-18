"""
generate_queries.py
-------------------
Reads processed_records.json and generates realistic industry-style
search queries based on actual indexed records.

Note: stdout is forced to utf-8 so accented characters print correctly
on Windows terminals.

Fields in processed_records.json:
    id, source, title, abstract, university, date,
    contributors, domain, is_indian, cpc_codes

Run (from the project root):
    python data/generate_queries.py

Output:
    data/sample_queries.json
"""

import json
import random
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Force UTF-8 output on Windows so accented chars and query text print correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent
RECORDS_FILE = SCRIPT_DIR / "processed_records.json"
OUTPUT_FILE  = SCRIPT_DIR / "sample_queries.json"

SAMPLE_SIZE  = 40   # number of records to generate queries from
CATEGORIES   = ["solve", "benchmark", "landscape"]

# ── Load env & client ─────────────────────────────────────────────────────────

load_dotenv(SCRIPT_DIR.parent / ".env")

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    sys.exit("Error: OPENAI_API_KEY not set. Add it to .env or export it.")

client = OpenAI(api_key=api_key)

# ── Load records ──────────────────────────────────────────────────────────────

print(f"Loading records from {RECORDS_FILE} ...")
with open(RECORDS_FILE, encoding="utf-8") as f:
    records = json.load(f)

print(f"  Loaded {len(records)} total records.")

# Sample with balanced distribution across domains
by_domain: dict[str, list] = {}
for r in records:
    by_domain.setdefault(r.get("domain", "Other"), []).append(r)

# Pick roughly equally from each domain, up to SAMPLE_SIZE total
sampled: list[dict] = []
domains = list(by_domain.keys())
per_domain = max(1, SAMPLE_SIZE // len(domains))
for d in domains:
    sampled.extend(random.sample(by_domain[d], min(per_domain, len(by_domain[d]))))

# Top up / trim to exact SAMPLE_SIZE
if len(sampled) < SAMPLE_SIZE:
    remaining = [r for r in records if r not in sampled]
    sampled.extend(random.sample(remaining, min(SAMPLE_SIZE - len(sampled), len(remaining))))
sampled = sampled[:SAMPLE_SIZE]
random.shuffle(sampled)

print(f"  Sampled {len(sampled)} records across {len(domains)} domains.\n")

# ── Prompt templates ──────────────────────────────────────────────────────────

CATEGORY_INSTRUCTIONS = {
    "solve": (
        "Write a query from the perspective of an industry company describing a specific "
        "technical problem they are trying to solve. Use business language, NOT academic language."
    ),
    "benchmark": (
        "Write a query asking to compare or evaluate two or more specific technologies or "
        "approaches that are relevant to this research area."
    ),
    "landscape": (
        "Write a query asking for an overview or survey of the research field this record "
        "belongs to — something a strategic analyst or R&D manager would ask."
    ),
}

PROMPT_TEMPLATE = """
You are helping an industry professional search for university research and patents on UniBridge.

Based on this academic record:
  Title:      {title}
  Domain:     {domain}
  Type:       {source}
  University: {university}
  Abstract:   {abstract}

Task: {instruction}

Rules:
- Write exactly ONE search query.
- Use natural, business-oriented language (not academic jargon).
- 1–2 sentences maximum.
- Do NOT mention the university name or the paper/patent title directly.
- Make it something a real company R&D team or tech-transfer officer would actually type.

Return ONLY the query text — no labels, no quotes, no explanation.
""".strip()

# ── Generation ────────────────────────────────────────────────────────────────

def generate_query(record: dict) -> dict:
    category = random.choice(CATEGORIES)
    abstract_excerpt = (record.get("abstract") or "")[:500]

    prompt = PROMPT_TEMPLATE.format(
        title       = record.get("title", "(untitled)"),
        domain      = record.get("domain", "Unknown"),
        source      = record.get("source", "unknown"),
        university  = record.get("university", "Unknown"),
        abstract    = abstract_excerpt,
        instruction = CATEGORY_INSTRUCTIONS[category],
    )

    response = client.chat.completions.create(
        model       = "gpt-3.5-turbo",
        messages    = [{"role": "user", "content": prompt}],
        max_tokens  = 120,
        temperature = 0.85,
    )

    query_text = response.choices[0].message.content.strip().strip('"').strip("'")

    return {
        "query":               query_text,
        "category":            category,
        "source_record_id":    record.get("id"),
        "source_record_title": record.get("title"),
        "source_domain":       record.get("domain"),
        "source_university":   record.get("university"),
        "source_type":         record.get("source"),
        "is_indian":           record.get("is_indian", False),
    }


def main():
    results: list[dict] = []

    for i, record in enumerate(sampled):
        try:
            result = generate_query(record)
            results.append(result)
            tag = f"[{i+1:02d}/{len(sampled)}]"
            print(f"{tag} {result['category'].upper():10s} {result['query'][:90]}")
        except Exception as exc:
            print(f"[{i+1:02d}/{len(sampled)}] ERROR — {exc}")

    # ── Save full output ───────────────────────────────────────────────────────
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("SAMPLE QUERIES BY CATEGORY")
    print("=" * 65)

    for cat in CATEGORIES:
        cat_qs = [r for r in results if r["category"] == cat]
        print(f"\n-- {cat.upper()} ({len(cat_qs)} queries) " + "-" * (40 - len(cat)))
        for q in cat_qs:
            print(f"  * {q['query']}")

    print(f"\nDone! Saved {len(results)} queries -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
