# M-09: Pure CLI Channel — Interactive Terminal Interface
import sys
import os

# Add project root to sys.path so modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m02_preprocessor      import preprocess
from modules.m03_synonym_expander   import expand_synonyms
from modules.m04_tfidf_retrieval    import retrieve
from modules.m05_intent_classifier  import classify_intent
from modules.m06_entity_extractor   import extract_entities
from modules.m07_context_manager    import update_context, enrich_with_context
from modules.m08_fallback_handler   import handle_fallback
from analytics.m10_analytics_logger import log_event
from config                         import CONFIDENCE_THRESHOLD

def process_query_cli(raw_query: str, session: dict) -> dict:
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
        "answer": answer,
        "intent": intent,
        "score": results[0]["score"] if results else 0.0,
        "status": status
    }

def main():
    print("==============================================")
    print("🎓 SIT EduBot CLI Activated")
    print("Type 'quit' or 'exit' to end.")
    print("Type 'whatsapp' to toggle WhatsApp simulator.")
    print("==============================================\n")
    
    session = {"history": []}
    whatsapp_mode = False
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
            
        if not user_input:
            continue
            
        cmd = user_input.lower()
        if cmd in ["quit", "exit"]:
            print("Goodbye!")
            break
        elif cmd == "whatsapp":
            whatsapp_mode = not whatsapp_mode
            print(f"[WhatsApp Mode {'ON' if whatsapp_mode else 'OFF'}]")
            continue
            
        response = process_query_cli(user_input, session)
        
        prefix = "🤖 EduBot: " if whatsapp_mode else "Bot: "
        print(f"\n{prefix}{response['answer']}")
        print(f"  [Dev Info] Intent: {response['intent']} | Match Score: {response['score']}\n")

if __name__ == "__main__":
    main()
