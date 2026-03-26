# M-07: Context Manager — multi-turn conversation state
from config import CONTEXT_WINDOW

_FOLLOWUP_TRIGGERS = {
    "that", "it", "this", "those", "same", "above", "what about", "and",
    "tell me more", "explain", "more details", "also", "additionally", "else"
}


def enrich_with_context(raw_query: str, tokens: list, session: dict) -> dict:
    """
    Detect follow-up questions and enrich token list with context from history.

    Returns a dict:
        "raw_query"   — original query
        "tokens"      — enriched token list
        "is_followup" — bool flag
    """
    history    = session.get("history", [])
    q_lower    = raw_query.lower()
    is_followup = any(trigger in q_lower for trigger in _FOLLOWUP_TRIGGERS)

    enriched_tokens = list(tokens)

    if is_followup and history:
        last_turn = history[-1]
        # Inject last intent as a pseudo-token (helps TF-IDF find relevant FAQs)
        if "intent" in last_turn and last_turn["intent"] != "unknown":
            enriched_tokens.append(last_turn["intent"])
        # Inject entity values as pseudo-tokens
        if "entities" in last_turn:
            for key, values in last_turn["entities"].items():
                enriched_tokens.extend([str(v) for v in values])

    return {
        "raw_query":   raw_query,
        "tokens":      enriched_tokens,
        "is_followup": is_followup
    }


def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    """
    Append the current turn to the session history, keeping a sliding window.
    """
    if "history" not in session:
        session["history"] = []

    session["history"].append({
        "query":    query,
        "answer":   answer,
        "intent":   intent,
        "entities": entities,
    })
    # Maintain sliding window
    session["history"] = session["history"][-CONTEXT_WINDOW:]
