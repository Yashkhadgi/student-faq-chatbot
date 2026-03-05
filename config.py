import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FAQ_PATH        = os.path.join(BASE_DIR, "data", "faqs.json")
SYNONYMS_PATH   = os.path.join(BASE_DIR, "data", "synonyms.json")
INTENTS_PATH    = os.path.join(BASE_DIR, "data", "intents.json")
ANALYTICS_LOG   = os.path.join(BASE_DIR, "analytics", "logs.csv")

TFIDF_TOP_N          = 3
CONFIDENCE_THRESHOLD = 0.25
CONTEXT_WINDOW       = 3

FALLBACK_CLARIFY  = "I'm not sure I understood. Could you rephrase?"
FALLBACK_ESCALATE = "Please contact support@university.edu"
