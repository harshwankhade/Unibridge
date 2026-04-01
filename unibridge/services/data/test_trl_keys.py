"""
test_trl_keys.py
----------------
Confirms that predict_trl_rules() ALWAYS returns a dict containing
exactly the four required keys: trl, confidence, matched_keywords, method,
regardless of input.

Covers:
  - Normal match (keywords found)
  - Zero-match default (no keywords → TRL 3, confidence 0.0)
  - Empty string
  - Whitespace-only string
  - Gibberish / numbers-only string
  - Very long abstract
  - Abstract that matches keywords in several TRL tiers simultaneously
"""

import sys
import os

# Allow running from any CWD
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from services.data.trl_classifier import predict_trl_rules, TRL_KEYWORDS

REQUIRED_KEYS = {"trl", "confidence", "matched_keywords", "method"}

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------
TEST_CASES = [
    # (label, abstract)
    ("normal – TRL 2 keywords",
     "This paper proposes a theoretical framework for quantum entanglement."),

    ("normal – TRL 3 keywords",
     "We ran controlled laboratory experiments confirming the proof of concept."),

    ("normal – TRL 9 keywords",
     "The system has been commercially deployed and is currently in production."),

    ("zero match default",
     "zzz xyz abc123 no keywords here at all."),

    ("empty string",
     ""),

    ("whitespace only",
     "     \t\n   "),

    ("numbers only",
     "1234567890 0987654321"),

    ("multi-tier overlap (TRL 3 + TRL 4 keywords)",
     "proof of concept validated in a controlled laboratory using an experimental setup."),

    ("very long abstract",
     ("This paper proposes a theoretical framework. " * 500).strip()),

    ("all TRL 1 keywords present",
     " ".join(kw for kw in TRL_KEYWORDS[1]["keywords"])),

    ("all TRL 9 keywords present",
     " ".join(kw for kw in TRL_KEYWORDS[9]["keywords"])),

    ("single character",
     "x"),

    ("unicode / non-ASCII",
     "αβγδ théorème fundamental von Grundlagen der Wissenschaft"),
]

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
PASS = "PASS"
FAIL = "FAIL"

results = []

for label, abstract in TEST_CASES:
    try:
        out = predict_trl_rules(abstract)
    except Exception as exc:
        results.append((FAIL, label, f"EXCEPTION: {exc}", None))
        continue

    issues = []

    # 1. Return type must be dict
    if not isinstance(out, dict):
        issues.append(f"return type is {type(out).__name__}, expected dict")
    else:
        # 2. All four keys present
        missing = REQUIRED_KEYS - out.keys()
        if missing:
            issues.append(f"missing keys: {sorted(missing)}")

        # 3. trl is int in range 1–9
        trl = out.get("trl")
        if not isinstance(trl, int) or not (1 <= trl <= 9):
            issues.append(f"trl={repr(trl)} is not an int in 1–9")

        # 4. confidence is float in 0.0–1.0
        conf = out.get("confidence")
        if not isinstance(conf, float) or not (0.0 <= conf <= 1.0):
            issues.append(f"confidence={repr(conf)} is not a float in [0.0, 1.0]")

        # 5. matched_keywords is a list of strings
        mk = out.get("matched_keywords")
        if not isinstance(mk, list):
            issues.append(f"matched_keywords is {type(mk).__name__}, expected list")
        elif any(not isinstance(k, str) for k in mk):
            issues.append("matched_keywords contains non-string items")

        # 6. method == "rules"
        if out.get("method") != "rules":
            issues.append(f"method={repr(out.get('method'))}, expected 'rules'")

    status = FAIL if issues else PASS
    results.append((status, label, "; ".join(issues) if issues else "", out))

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)

print("=" * 65)
print("TRL RETURN-KEYS VALIDATION")
print("=" * 65)
print(f"Cases run: {len(results)}  |  Passed: {passed}  |  Failed: {failed}")
print()

for status, label, issue, out in results:
    marker = "[OK]  " if status == PASS else "[FAIL]"
    print(f"  {marker} {label}")
    if issue:
        print(f"         -> {issue}")
    elif out:
        # Show the returned dict compactly on pass
        mk_preview = out['matched_keywords'][:3]
        ellipsis = "…" if len(out['matched_keywords']) > 3 else ""
        print(f"         trl={out['trl']}  conf={out['confidence']}  "
              f"matched={mk_preview}{ellipsis}  method={out['method']!r}")

print()
print("=" * 65)
if failed:
    print(f"RESULT: FAILED ({failed} case(s))")
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED")
    sys.exit(0)
