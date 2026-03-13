# M-07: Context Manager
# Owner: Member C
# Purpose: Maintain session history and resolve follow-up queries.
# Example: "What about the fee for THAT?" → resolves "that" = CS-301 from previous turn

from config import CONTEXT_WINDOW

def enrich_with_context(raw_query: str, tokens: list, session: dict) -> dict:
    """
    Checks session history for context clues.
    If follow-up detected, injects previous entities/intent into tokens.
    """
    history = session.get("history", [])

    # Keywords that signal a follow-up question
    followup_triggers = ["that", "it", "this", "those", "same", "above", "what about", "and"]

    is_followup = any(trigger in raw_query.lower() for trigger in followup_triggers)

    enriched_tokens = list(tokens)

    if is_followup and history:
        last_turn = history[-1]

        # Inject previous intent as a token
        if "intent" in last_turn:
            enriched_tokens.append(last_turn["intent"])

        # Inject previous entities as tokens
        if "entities" in last_turn:
            for key, values in last_turn["entities"].items():
                enriched_tokens.extend(values)

    return {
        "raw_query": raw_query,
        "tokens":    enriched_tokens,
        "is_followup": is_followup
    }


def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    """
    Adds current turn to session history.
    Keeps only last CONTEXT_WINDOW turns.
    """
    if "history" not in session:
        session["history"] = []

    session["history"].append({
        "query":    query,
        "answer":   answer,
        "intent":   intent,
        "entities": entities
    })

    # Keep only last N turns
    session["history"] = session["history"][-CONTEXT_WINDOW:]
