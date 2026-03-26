# M-07: Context Manager — multi-turn conversation state

last_intent = "unknown"

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
    global last_intent
    
    q_lower    = raw_query.lower()
    is_followup = any(trigger in q_lower for trigger in _FOLLOWUP_TRIGGERS)

    enriched_tokens = list(tokens)

    if is_followup and last_intent != "unknown":
        # Inject global last intent as pseudo-token
        enriched_tokens.append(last_intent)

    return {
        "raw_query":   raw_query,
        "tokens":      enriched_tokens,
        "is_followup": is_followup
    }


def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    """
    Update global intent for next follow-up.
    """
    global last_intent
    if intent and intent != "unknown":
        last_intent = intent
