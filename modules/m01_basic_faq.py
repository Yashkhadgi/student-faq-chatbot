# M-01: Basic FAQ Responder — cached + keyword-scored fast path
import json
import re
from config import FAQ_PATH

# ── Cache on module load ──────────────────────────────────────────────────────
with open(FAQ_PATH, "r") as _f:
    _FAQS = json.load(_f)

def _keyword_score(query_lower: str, faq: dict) -> float:
    """
    Score an FAQ against the query using keyword / tag overlap.
    Returns a float in [0.0, 1.0].
    """
    tags = faq.get("tags", [])
    if not tags:
        return 0.0
    # Exact-match tag hits
    hits = sum(1 for tag in tags if tag in query_lower)
    # Bonus: full phrase from question appears in query
    bonus = 0.2 if any(word in query_lower for word in faq["question"].lower().split()
                       if len(word) > 3) else 0.0
    raw = hits / len(tags) + bonus
    return min(round(raw, 4), 1.0)

def basic_faq_lookup(query: str) -> dict | None:
    """
    Search the FAQ cache for a confident match.
    Returns a dict with keys {faq, score} or None if no match found.
    """
    query_lower = query.lower()
    best_faq   = None
    best_score = 0.0

    for faq in _FAQS:
        score = _keyword_score(query_lower, faq)
        if score > best_score:
            best_score = score
            best_faq   = faq

    if best_faq and best_score > 0.0:
        return {"faq": best_faq, "score": best_score}
    return None
