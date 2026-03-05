from modules.m02_preprocessor      import preprocess
from modules.m03_synonym_expander   import expand_synonyms
from modules.m04_tfidf_retrieval    import retrieve
from modules.m05_intent_classifier  import classify_intent
from modules.m06_entity_extractor   import extract_entities
from modules.m07_context_manager    import update_context, enrich_with_context
from modules.m08_fallback_handler   import handle_fallback
from analytics.m10_analytics_logger import log_event
from config import CONFIDENCE_THRESHOLD

def process_query(raw_query: str, session: dict) -> dict:
    tokens          = preprocess(raw_query)
    enriched        = enrich_with_context(raw_query, tokens, session)
    expanded_tokens = expand_synonyms(enriched["tokens"])
    intent          = classify_intent(enriched["tokens"])
    entities        = extract_entities(raw_query)
    results         = retrieve(expanded_tokens)

    if results and results[0]["score"] >= CONFIDENCE_THRESHOLD:
        answer = results[0]["answer"]
        status = "answered"
    else:
        answer = handle_fallback(raw_query, results)
        status = "fallback"

    update_context(session, raw_query, answer, intent, entities)
    log_event(raw_query, intent, entities, results[0]["score"] if results else 0, status)

    return {
        "answer":      answer,
        "intent":      intent,
        "entities":    entities,
        "status":      status,
        "top_matches": results
    }

if __name__ == "__main__":
    session = {"history": []}
    print("Student FAQ Chatbot — type 'exit' to quit\n")
    while True:
        query = input("You: ").strip()
        if query.lower() == "exit":
            break
        response = process_query(query, session)
        print(f"Bot: {response['answer']}\n")
