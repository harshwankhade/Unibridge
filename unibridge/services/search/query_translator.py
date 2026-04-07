"""
query_translator.py
-------------------
Translates plain business-language queries into academic/patent search
terminology using OpenAI GPT-3.5 Turbo.

Three search categories are supported:
  - solve      : user has a technical problem to solve
  - benchmark  : user wants to compare technologies
  - landscape  : user wants an overview of a technical field

Usage:
    from query_translator import translate_query
    result = translate_query("battery degradation in EV fleets", "solve")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (three levels up: services/search/ → root)
try:
    _ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=_ENV_PATH, override=False)
except IndexError:
    pass

# ---------------------------------------------------------------------------
# Step 1 — Imports and client setup
# ---------------------------------------------------------------------------
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Step 2 — Category-aware system prompts
# ---------------------------------------------------------------------------
SYSTEM_PROMPTS = {
    "solve": """You are an expert at translating business problems into academic and \
patent search queries. The user has a specific technical problem they want to solve.
Your job is to rewrite their query using precise technical, scientific, and patent \
terminology that would appear in university research papers and patent abstracts.
Focus on: technical mechanisms, scientific principles, and solution approaches.""",

    "benchmark": """You are an expert at translating technology comparison requests \
into academic and patent search queries. The user wants to benchmark or compare \
technologies in a specific area.
Your job is to rewrite their query using precise technical terminology that would \
appear in comparative studies, review papers, and patent classifications.
Focus on: performance metrics, technical specifications, and competing approaches.""",

    "landscape": """You are an expert at translating broad technology interest into \
academic and patent search queries. The user wants to explore the overall landscape \
of a technical field.
Your job is to rewrite their query into broader technical terminology that captures \
the full scope of research and patents in that domain.
Focus on: field-defining terms, subdomains, and foundational concepts.""",
}

_VALID_CATEGORIES = set(SYSTEM_PROMPTS.keys())

# ---------------------------------------------------------------------------
# Step 3 — translate_query
# ---------------------------------------------------------------------------

def translate_query(query: str, category: str) -> dict:
    """
    Translate a plain-language business query into academic/patent terminology.

    Parameters
    ----------
    query    : raw user query string
    category : one of "solve", "benchmark", "landscape"
               (defaults to "solve" if invalid)

    Returns
    -------
    dict with keys:
        original_query   – original query unchanged
        translated_query – GPT-translated query (or original on failure)
        category         – normalised category string used
    """
    # 1. Validate / default category
    if category not in _VALID_CATEGORIES:
        category = "solve"

    # 2. Select system prompt
    system_prompt = SYSTEM_PROMPTS[category]

    # 3. Build user message
    user_message = (
        f"Translate this query into academic and patent search terminology.\n\n"
        f"Original query: {query}\n\n"
        f"Return ONLY the translated query as a single paragraph. "
        f"No explanation, no bullet points, no preamble."
    )

    # 4. Call OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=150,
            temperature=0.3,
        )

        # 5 & 6. Extract and strip
        translated = response.choices[0].message.content.strip()

    except Exception as exc:  # noqa: BLE001
        # 7. Fallback — return original query unchanged
        print(f"[translate_query] OpenAI error: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        translated = query

    return {
        "original_query":   query,
        "translated_query": translated,
        "category":         category,
    }


# ---------------------------------------------------------------------------
# Step 4 — Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        ("We are struggling with battery degradation in our EV fleet",       "solve"),
        ("We want to compare different water purification technologies",       "benchmark"),
        ("Give us an overview of the quantum computing space",                "landscape"),
    ]

    for query, category in test_cases:
        result = translate_query(query, category)
        print(f"Category : {result['category']}")
        print(f"Original : {result['original_query']}")
        print(f"Translated: {result['translated_query']}")
        print()
