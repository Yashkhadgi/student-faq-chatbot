# M-08: Fallback Handler
from config import FALLBACK_CLARIFY, FALLBACK_ESCALATE

def handle_fallback(query: str, candidates: list) -> str:
    if not candidates:
        return FALLBACK_CLARIFY
    top_candidates = [c for c in candidates if c["score"] > 0.05]
    if top_candidates:
        suggestions = "\n".join([f"  {i+1}. {c['question']}" for i, c in enumerate(top_candidates[:2])])
        return f"I'm not sure I understood. Did you mean:\n{suggestions}\nPlease rephrase or choose one of the above."
    return FALLBACK_ESCALATE
