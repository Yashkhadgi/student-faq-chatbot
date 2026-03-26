# app.py — Flask REST API + pipeline orchestrator
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from modules.m01_basic_faq       import basic_faq_lookup
from modules.m02_preprocessor    import preprocess
from modules.m03_synonym_expander import expand_synonyms
from modules.m04_tfidf_retrieval  import retrieve
from modules.m05_intent_classifier import classify_intent
from modules.m06_entity_extractor  import extract_entities, enrich_answer_with_entities
from modules.m07_context_manager   import update_context, enrich_with_context
from modules.m08_fallback_handler  import handle_fallback
from analytics.m10_analytics_logger import log_event, get_recent_logs, get_analytics_summary
from utils.helpers import load_faqs
from config import (
    CONFIDENCE_THRESHOLD, M01_FAST_PATH_SCORE,
    FRONTEND_DIR, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
)

# ── Flask setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# In-memory session store (keyed by session_id)
_sessions: dict[str, dict] = {}


# ── Pipeline ───────────────────────────────────────────────────────────────────
def process_query(raw_query: str, session: dict, session_id: str = "") -> dict:
    """
    Full chatbot pipeline:
      1. M01 fast path — if keyword score ≥ M01_FAST_PATH_SCORE, return immediately
      2. M02 preprocess
      3. M07 context enrichment
      4. M03 synonym expansion
      5. M05 intent classification
      6. M06 entity extraction
      7. M04 TF-IDF retrieval
      8. Confidence threshold → answer or M08 fallback
      9. M07 context update
      10. M10 log event
    """

    # ── STEP 1: M01 Fast Path ────────────────────────────────────────────────
    m01_result = basic_faq_lookup(raw_query)
    if m01_result and m01_result["score"] >= M01_FAST_PATH_SCORE:
        faq    = m01_result["faq"]
        intent = faq.get("intent", "unknown")
        entities = extract_entities(raw_query)
        answer = enrich_answer_with_entities(faq["answer"], entities)
        update_context(session, raw_query, answer, intent, entities)
        log_event(raw_query, intent, entities, m01_result["score"], "m01_fast", session_id)
        return {
            "answer":      answer,
            "intent":      intent,
            "entities":    entities,
            "status":      "m01_fast",
            "confidence":  m01_result["score"],
            "top_matches": [{"id": faq["id"], "question": faq["question"],
                             "answer": faq["answer"], "score": m01_result["score"]}],
        }

    # ── STEP 2: Preprocess ───────────────────────────────────────────────────
    preprocessed    = preprocess(raw_query)
    tokens          = preprocessed["tokens"]

    # ── STEP 3: Context enrichment ───────────────────────────────────────────
    enriched        = enrich_with_context(raw_query, tokens, session)

    # ── STEP 4: Synonym expansion ────────────────────────────────────────────
    expanded_tokens = expand_synonyms(enriched["tokens"])

    # ── STEP 5: Intent classification ───────────────────────────────────────
    intent          = classify_intent(enriched["tokens"])

    # ── STEP 6: Entity extraction ────────────────────────────────────────────
    entities        = extract_entities(raw_query)

    # ── STEP 7: TF-IDF retrieval ─────────────────────────────────────────────
    results         = retrieve(expanded_tokens)

    # ── STEP 8: Threshold decision ───────────────────────────────────────────
    if results and results[0]["score"] >= CONFIDENCE_THRESHOLD:
        raw_answer = results[0]["answer"]
        answer     = enrich_answer_with_entities(raw_answer, entities)
        status     = "answered"
        confidence = results[0]["score"]
    else:
        answer     = handle_fallback(raw_query, results)
        status     = "fallback"
        confidence = results[0]["score"] if results else 0.0

    # ── STEP 9: Update context ───────────────────────────────────────────────
    update_context(session, raw_query, answer, intent, entities)

    # ── STEP 10: Log event ───────────────────────────────────────────────────
    log_event(raw_query, intent, entities, confidence, status, session_id)

    return {
        "answer":      answer,
        "intent":      intent,
        "entities":    entities,
        "status":      status,
        "confidence":  round(confidence, 4),
        "top_matches": results,
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check."""
    return jsonify({"status": "ok", "service": "SIT EduBot"})


@app.route("/api/faqs", methods=["GET"])
def faqs():
    """Return all FAQ questions."""
    all_faqs = load_faqs()
    return jsonify([
        {"id": f["id"], "question": f["question"], "intent": f.get("intent", "")}
        for f in all_faqs
    ])


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Accept a chat message and return the bot response.

    Request body (JSON):
        query      — the user's message (required)
        session_id — client session UUID (optional, auto-generated if missing)

    Response (JSON):
        answer, intent, entities, status, confidence, top_matches, session_id
    """
    data = request.get_json(force=True, silent=True) or {}
    raw_query  = (data.get("query") or "").strip()
    session_id = (data.get("session_id") or str(uuid.uuid4()))

    if not raw_query:
        return jsonify({"error": "query is required"}), 400

    # Retrieve or create session
    if session_id not in _sessions:
        _sessions[session_id] = {"history": []}
    session = _sessions[session_id]

    response = process_query(raw_query, session, session_id)
    response["session_id"] = session_id
    return jsonify(response)


@app.route("/api/analytics", methods=["GET"])
def analytics():
    """Return last 50 log entries + summary stats."""
    limit = int(request.args.get("limit", 50))
    logs    = get_recent_logs(limit)
    summary = get_analytics_summary()
    return jsonify({"logs": logs, "summary": summary})


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🎓 SIT EduBot — Flask server starting on http://localhost:5000")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
