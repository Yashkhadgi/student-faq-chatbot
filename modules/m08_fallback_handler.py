# M-08: Fallback Handler
# Owner: Member C
# Purpose: Handle low-confidence retrievals with 3-tier fallback
# Tier 1: Ask for clarification
# Tier 2: Suggest closest FAQ matches
# Tier 3: Escalate to human advisor

from config import CONFIDENCE_THRESHOLD, FALLBACK_CLARIFY, FALLBACK_ESCALATE

def handle_fallback(query: str, candidates: list) -> str:
    """
    3-tier fallback logic:
    - Tier 1: No candidates at all → ask to rephrase
    - Tier 2: Low score candidates exist → suggest them
    - Tier 3: Nothing useful at all → escalate to human
    """

    # Tier 1 — No results returned at all
    if not candidates:
        return FALLBACK_CLARIFY

    # Tier 2 — Results exist but confidence is low → suggest top matches
    top_candidates = [c for c in candidates if c["score"] > 0.05]

    if top_candidates:
        suggestions = "\n".join([
            f"  {i+1}. {c['question']}"
            for i, c in enumerate(top_candidates[:2])
        ])
        return (
            f"I'm not sure I understood your question. Did you mean:\n"
            f"{suggestions}\n"
            f"Please rephrase or choose one of the above."
        )

    # Tier 3 — Nothing useful → escalate
    return FALLBACK_ESCALATE
