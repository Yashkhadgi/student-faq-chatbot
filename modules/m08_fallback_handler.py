# M-08: Fallback Handler — SIT Nagpur branding + WhatsApp routing
from config import FALLBACK_CLARIFY, FALLBACK_ESCALATE

_LOW_CONFIDENCE_THRESHOLD = 0.05


def handle_fallback(query: str, candidates: list) -> str:
    """
    Determine the best fallback response:
      1. If no candidates at all → restate / ask to rephrase
      2. If there are low-confidence candidates → suggest top 2 questions
      3. If even suggestions are empty → escalate to SIT helpdesk

    Args:
        query:      The original user query (unused in message but available for future use)
        candidates: List of TF-IDF result dicts with 'question' and 'score' keys

    Returns:
        A human-readable fallback string.
    """
    if not candidates:
        return FALLBACK_CLARIFY

    # Filter candidates that have at least a tiny signal
    weak_candidates = [c for c in candidates if c["score"] > _LOW_CONFIDENCE_THRESHOLD]

    # Emergency escalation bypass
    q_lower = query.lower()
    emergency_keywords = ["urgent", "emergency", "stuck", "help", "problem", "issue"]
    if any(word in q_lower for word in emergency_keywords):
        return FALLBACK_ESCALATE

    if weak_candidates:
        suggestion_lines = "\n".join(
            f"  {i + 1}. {c['question']}"
            for i, c in enumerate(weak_candidates[:2])
        )
        return (
            "🤔 I'm not quite sure I understood your question. "
            "Did you mean one of these?\n\n"
            f"{suggestion_lines}\n\n"
            "Please rephrase your question or choose one of the above."
        )

    # Full escalation to SIT helpdesk
    return FALLBACK_ESCALATE
