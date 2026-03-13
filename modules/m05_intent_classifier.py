# M-05: Intent Classifier
# Owner: Member B
def classify_intent(tokens: list) -> str:
    intent_keywords = {
        "fee":        ["fee", "tuition", "cost", "charges", "payment"],
        "exam":       ["exam", "test", "assessment", "paper"],
        "admission":  ["admission", "apply", "enrollment", "registration"],
        "hostel":     ["hostel", "accommodation", "dorm"],
        "schedule":   ["timetable", "schedule", "timing", "class"],
        "result":     ["result", "marks", "grades", "score"],
        "contact":    ["contact", "email", "phone", "reach"],
        "scholarship":["scholarship", "financial", "grant"],
        "attendance": ["attendance", "present", "regularity"]
    }
    for intent, keywords in intent_keywords.items():
        if any(token in keywords for token in tokens):
            return intent
    return "unknown"
