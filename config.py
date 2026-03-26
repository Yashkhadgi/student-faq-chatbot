import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FAQ_PATH        = os.path.join(BASE_DIR, "data", "faqs.json")
SYNONYMS_PATH   = os.path.join(BASE_DIR, "data", "synonyms.json")
INTENTS_PATH    = os.path.join(BASE_DIR, "data", "intents.json")
ANALYTICS_LOG   = os.path.join(BASE_DIR, "analytics", "logs.csv")
FRONTEND_DIR    = os.path.join(BASE_DIR, "frontend")

TFIDF_TOP_N          = 3
CONFIDENCE_THRESHOLD = 0.25
M01_FAST_PATH_SCORE  = 0.8   # M01 confidence threshold to skip TF-IDF
CONTEXT_WINDOW       = 3

FALLBACK_CLARIFY  = "I'm not sure I understood your question. Could you please rephrase it?"
FALLBACK_ESCALATE = (
    "I wasn't able to find an answer to your question. "
    "Please contact the SIT Nagpur helpdesk:\n"
    "📧 helpdesk@sitng.ac.in\n"
    "📞 +91-712-2223344\n"
    "💬 WhatsApp: https://wa.me/917122223344\n"
    "Office timings: Mon–Sat, 9AM–5PM"
)

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001  # 5000 is taken by macOS AirPlay Receiver
FLASK_DEBUG = True
