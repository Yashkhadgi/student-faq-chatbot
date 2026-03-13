import json
from config import FAQ_PATH, SYNONYMS_PATH, INTENTS_PATH

def load_faqs():
    with open(FAQ_PATH, "r") as f:
        return json.load(f)

def load_synonyms():
    with open(SYNONYMS_PATH, "r") as f:
        return json.load(f)

def load_intents():
    with open(INTENTS_PATH, "r") as f:
        return json.load(f)
