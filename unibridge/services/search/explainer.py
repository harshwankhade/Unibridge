"""
explainer.py
------------
Generates a one-sentence relevance explanation for each search result,
connecting it back to the original business query using OpenAI GPT-3.5 Turbo.

The explanations are attached in-place to the result dicts so the list can
be passed directly through the search pipeline.

Usage:
    from explainer import explain_results
    results = explain_results(query, results, category)
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

_SYSTEM_MESSAGE = (
    "You are an expert at explaining why a research paper or patent is relevant "
    "to a business query. Be concise and specific. Always respond in one sentence only."
)

_FALLBACK_EXPLANATION = "Relevant to your query based on semantic similarity."


# ---------------------------------------------------------------------------
# Step 2 — explain_results
# ---------------------------------------------------------------------------

def explain_results(
    query: str,
    results: list[dict],
    category: str,
) -> list[dict]:
    """
    Attach a one-sentence relevance explanation to each result dict.

    Parameters
    ----------
    query    : original plain-language user query (not the translated one)
    results  : re-ranked result list from retriever.py
    category : search category — "solve", "benchmark", or "landscape"

    Returns
    -------
    Same results list with `explanation` key added to every dict.
    """
    for result in results:
        title    = result.get("title", "")
        abstract = result.get("abstract", "")[:300]

        user_message = (
            f"Business query: {query}\n"
            f"Search category: {category}\n\n"
            f"Title: {title}\n"
            f"Abstract: {abstract}\n\n"
            f"In one sentence, explain why this result is relevant to the query above. "
            f"Focus on the specific connection between the user's need and this research."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": _SYSTEM_MESSAGE},
                    {"role": "user",   "content": user_message},
                ],
                max_tokens=80,
                temperature=0.3,
            )
            explanation = response.choices[0].message.content.strip()

        except Exception as exc:  # noqa: BLE001
            print(
                f"[explain_results] OpenAI error for '{title[:40]}...': "
                f"{type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            explanation = _FALLBACK_EXPLANATION

        result["explanation"] = explanation

    return results


# ---------------------------------------------------------------------------
# Step 3 — Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dummy_results = [
        {
            "title": "Solid-state electrolytes for lithium-ion battery longevity",
            "abstract": (
                "This paper investigates the use of solid-state electrolytes to reduce "
                "capacity degradation in lithium-ion batteries under repeated charge cycles. "
                "Experimental results show 40% improvement in cycle life."
            ),
            "university": "MIT",
            "source":     "paper",
            "domain":     "Chemistry & Materials",
            "trl":        4,
        },
        {
            "title": "Machine learning prediction of battery degradation patterns",
            "abstract": (
                "We propose a neural network model trained on real-world EV battery "
                "telemetry data to predict degradation trajectories and recommend optimal "
                "charging strategies."
            ),
            "university": "Stanford University",
            "source":     "paper",
            "domain":     "Computing & AI",
            "trl":        5,
        },
    ]

    query    = "We are struggling with battery degradation in our EV fleet"
    category = "solve"

    results = explain_results(query, dummy_results, category)
    for r in results:
        print(f"Title      : {r['title']}")
        print(f"Explanation: {r['explanation']}")
        print()
