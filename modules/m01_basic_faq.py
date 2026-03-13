# M-01: Basic FAQ Responder
import json
from config import FAQ_PATH

def basic_faq_lookup(query: str):
    with open(FAQ_PATH, "r") as f:
        faqs = json.load(f)
    query_lower = query.lower()
    for faq in faqs:
        if any(tag in query_lower for tag in faq["tags"]):
            return faq
    return None
