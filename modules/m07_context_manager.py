# M-07: Context Manager
from config import CONTEXT_WINDOW

def enrich_with_context(raw_query: str, tokens: list, session: dict) -> dict:
    history = session.get("history", [])
    followup_triggers = ["that", "it", "this", "those", "same", "above", "what about", "and"]
    is_followup = any(trigger in raw_query.lower() for trigger in followup_triggers)
    enriched_tokens = list(tokens)
    if is_followup and history:
        last_turn = history[-1]
        if "intent" in last_turn:
            enriched_tokens.append(last_turn["intent"])
        if "entities" in last_turn:
            for key, values in last_turn["entities"].items():
                enriched_tokens.extend(values)
    return {"raw_query": raw_query, "tokens": enriched_tokens, "is_followup": is_followup}

def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    if "history" not in session:
        session["history"] = []
    session["history"].append({"query": query, "answer": answer, "intent": intent, "entities": entities})
    session["history"] = session["history"][-CONTEXT_WINDOW:]
