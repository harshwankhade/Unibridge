"""
trl_classifier.py
-----------------
Technology Readiness Level (TRL) predictor — two strategies:

  predict_trl_rules(abstract)  – fast, offline, keyword-based
  predict_trl_llm(abstract)    – Gemini Flash LLM, requires GEMINI_API_KEY

TRL scale:
  1 – Basic principles observed (purely theoretical)
  2 – Technology concept formulated
  3 – Experimental proof of concept
  4 – Technology validated in lab
  5 – Technology validated in relevant environment
  6 – Technology demonstrated in relevant environment
  7 – System prototype in operational environment
  8 – System complete and qualified (pre-commercial)
  9 – Proven in operational environment (commercial)

Usage:
    from services.data.trl_classifier import predict_trl_rules, predict_trl_llm
    rules_result = predict_trl_rules(abstract_text)
    llm_result   = predict_trl_llm(abstract_text)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load .env from project root — two levels up from services/data/
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# ---------------------------------------------------------------------------
# OpenAI client — reads OPENAI_API_KEY from the environment / .env
# ---------------------------------------------------------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Step 1 — Weighted keyword lists per TRL tier
# ---------------------------------------------------------------------------

TRL_KEYWORDS: dict[int, dict] = {
    1: {
        "keywords": [
            "theoretical",
            "hypothesis",
            "fundamental",
            "basic principles",
            "conceptual",
            "proposed theory",
            "initial investigation",
            "literature review",
            "mathematical model",
            "analytical framework",
        ],
        "weight": 1.0,
    },
    2: {
        "keywords": [
            "concept formulated",
            "feasibility",
            "proposed approach",
            "preliminary design",
            "potential application",
            "speculative",
            "conceptual design",
            "we propose",
            "this paper proposes",
            "novel concept",
            "theoretical framework",
        ],
        "weight": 1.0,
    },
    3: {
        "keywords": [
            "proof of concept",
            "experimental validation",
            "laboratory experiment",
            "bench test",
            "simulation results",
            "first demonstration",
            "small scale experiment",
            "controlled experiment",
            "in vitro",
            "initial results show",
            "experiments confirm",
        ],
        "weight": 1.0,
    },
    4: {
        "keywords": [
            "lab scale",
            "laboratory prototype",
            "laboratory testing",
            "validated in lab",
            "component testing",
            "breadboard",
            "in vitro testing",
            "controlled laboratory",
            "bench scale",
            "lab environment",
            "experimental setup",
        ],
        "weight": 1.0,
    },
    5: {
        "keywords": [
            "relevant environment",
            "pilot study",
            "pilot scale",
            "simulated environment",
            "integrated system tested",
            "field test",
            "semi-industrial",
            "scaled up",
            "in vivo",
            "preliminary field",
            "prototype tested",
        ],
        "weight": 1.0,
    },
    6: {
        "keywords": [
            "prototype demonstrated",
            "system prototype",
            "field demonstration",
            "representative environment",
            "full scale prototype",
            "demonstrated performance",
            "technology demonstrator",
            "operational prototype",
            "advanced prototype",
        ],
        "weight": 1.0,
    },
    7: {
        "keywords": [
            "operational environment",
            "real-world deployment",
            "field trial",
            "system demonstration",
            "operational test",
            "end-to-end system",
            "technology demonstrated operationally",
            "pilot deployment",
            "real environment",
            "user trial",
        ],
        "weight": 1.0,
    },
    8: {
        "keywords": [
            "system qualified",
            "pre-commercial",
            "final testing",
            "ready for deployment",
            "certification",
            "regulatory approval",
            "manufacturing ready",
            "fully integrated",
            "production ready",
            "clinical trial",
            "commercialization ready",
        ],
        "weight": 1.0,
    },
    9: {
        "keywords": [
            "commercially deployed",
            "in production",
            "operational system",
            "proven technology",
            "fully deployed",
            "commercial product",
            "adopted by industry",
            "currently used",
            "market deployed",
            "in use",
            "successfully deployed",
            "licensed to",
        ],
        "weight": 1.0,
    },
}

# ---------------------------------------------------------------------------
# Step 2 — Prediction function
# ---------------------------------------------------------------------------

def predict_trl_rules(abstract: str) -> dict:
    """
    Predict the TRL of a research record using weighted keyword matching.

    Parameters
    ----------
    abstract : str
        The abstract (or any descriptive text) to classify.

    Returns
    -------
    dict with keys:
        trl              – int, predicted TRL level (1–9)
        confidence       – float, fraction of total score held by winning tier
        matched_keywords – list[str], keywords that matched for the winning tier
        method           – str, always "rules"
    """
    text = abstract.lower()

    # Count keyword hits and compute raw scores per TRL
    raw_scores: dict[int, float] = {}
    hits: dict[int, list[str]] = {}

    for trl, config in TRL_KEYWORDS.items():
        matched = [kw for kw in config["keywords"] if kw in text]
        raw_scores[trl] = len(matched) * config["weight"]
        hits[trl] = matched

    total_score = sum(raw_scores.values())

    if total_score == 0:
        # No keywords matched — default to TRL 3 (earliest experimental stage)
        return {
            "trl": 3,
            "confidence": 0.0,
            "matched_keywords": [],
            "method": "rules",
        }

    # Winning TRL = highest raw score (ties broken by lower TRL — more conservative)
    predicted_trl = max(raw_scores, key=lambda t: (raw_scores[t], -t))

    confidence = round(raw_scores[predicted_trl] / total_score, 2)

    return {
        "trl": predicted_trl,
        "confidence": confidence,
        "matched_keywords": hits[predicted_trl],
        "method": "rules",
    }

# ---------------------------------------------------------------------------
# LLM-based prediction  (Gemini Flash)
# ---------------------------------------------------------------------------

_TRL_PROMPT_TEMPLATE = """\
You are a Technology Readiness Level (TRL) expert. Given a patent or research \
paper abstract, predict its TRL level on a scale of 1 to 9.

TRL Scale:
1 - Basic principles observed (purely theoretical)
2 - Technology concept formulated (hypothesis, not yet tested)
3 - Experimental proof of concept (first lab experiments)
4 - Technology validated in lab (lab-scale testing)
5 - Technology validated in relevant environment (pilot testing)
6 - Technology demonstrated in relevant environment (prototype tested)
7 - System prototype in operational environment (real-world trial)
8 - System complete and qualified (pre-commercial)
9 - Proven in operational environment (fully deployed, commercial)

Abstract:
{abstract}

Respond ONLY with a valid JSON object and nothing else. No explanation outside the JSON.
Format:
{{
  "trl": <integer 1-9>,
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": <one sentence explaining why>
}}
"""

_FALLBACK_LLM: dict = {
    "trl": 3,
    "confidence": 0.0,
    "reasoning": "LLM prediction failed — fallback to default",
    "method": "llm",
}


def predict_trl_llm(abstract: str) -> dict:
    """
    Predict TRL using the Gemini 1.5 Flash model.

    Parameters
    ----------
    abstract : str
        The abstract (or any descriptive text) to classify.

    Returns
    -------
    dict with keys:
        trl       – int, predicted TRL level (1–9)
        confidence – float (0.0–1.0), model's self-reported certainty
        reasoning  – str, one-sentence rationale from the model
        method     – str, always "llm"

    Notes
    -----
    On any failure (network error, invalid JSON, missing fields) the function
    returns the _FALLBACK_LLM sentinel rather than raising an exception.
    """
    try:
        prompt = _TRL_PROMPT_TEMPLATE.format(abstract=abstract)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw_text = response.choices[0].message.content.strip()

        # Strip optional markdown code fences (```json … ```)
        if raw_text.startswith("```"):
            lines    = raw_text.splitlines()
            raw_text = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            ).strip()

        data = json.loads(raw_text)

        # --- Validate presence of required fields ---
        required = {"trl", "confidence", "reasoning"}
        missing  = required - data.keys()
        if missing:
            raise ValueError(f"Response missing fields: {missing}")

        # --- Sanitise and clamp values ---
        trl        = int(data["trl"])
        trl        = max(1, min(9, trl))          # clamp to [1, 9]

        confidence = float(data["confidence"])
        confidence = round(max(0.0, min(1.0, confidence)), 2)  # clamp to [0, 1]

        reasoning  = str(data["reasoning"]).strip()

        return {
            "trl":       trl,
            "confidence": confidence,
            "reasoning":  reasoning,
            "method":     "llm",
        }

    except Exception as e:  # noqa: BLE001
        print(f"[predict_trl_llm] API error: {type(e).__name__}: {e}")
        return dict(_FALLBACK_LLM)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        "This paper proposes a theoretical framework for quantum entanglement.",
        "We validated our approach through controlled laboratory experiments on a bench-scale prototype.",
        "The system has been commercially deployed in three industrial facilities and is currently in production.",
    ]

    print("--- Rule-based predictions ---")
    for abstract in test_cases:
        result = predict_trl_rules(abstract)
        print(abstract[:80])
        print(result)
        print()

    print("--- LLM predictions ---")
    for abstract in test_cases:
        result = predict_trl_llm(abstract)
        print(abstract[:80])
        print(result)
        print()
