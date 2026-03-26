# M-05: Intent Classifier — TF-IDF + Logistic Regression, with keyword fallback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from utils.helpers import load_intents

_ML_CONFIDENCE_THRESHOLD = 0.5

# ── Build training data from intents.json ─────────────────────────────────────
_intents_data = load_intents()
_train_texts:  list[str] = []
_train_labels: list[str] = []

for intent_obj in _intents_data.get("intents", []):
    label    = intent_obj["label"]
    examples = intent_obj.get("examples", [])
    for example in examples:
        _train_texts.append(example)
        _train_labels.append(label)

# Fit classifier at module load
_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
_X   = _vec.fit_transform(_train_texts)
_clf = LogisticRegression(max_iter=500, C=5.0)
_clf.fit(_X, _train_labels)

# ── Keyword fallback ──────────────────────────────────────────────────────────
_KEYWORD_MAP = {
    "fee":        ["fee", "fees", "tuition", "cost", "charges", "payment"],
    "exam":       ["exam", "exams", "test", "assessment", "paper", "examination"],
    "admission":  ["admission", "apply", "enrollment", "registration", "joining"],
    "hostel":     ["hostel", "accommodation", "dorm", "dormitory", "room", "stay"],
    "schedule":   ["timetable", "schedule", "timing", "class", "slots", "routine"],
    "result":     ["result", "marks", "grades", "score", "grade"],
    "contact":    ["contact", "email", "phone", "reach", "helpdesk", "call"],
    "scholarship":["scholarship", "financial", "grant", "aid", "bursary"],
    "attendance": ["attendance", "present", "regularity", "75"],
    "library":    ["library", "books", "read", "timings", "open", "reading"],
}


def _keyword_fallback(tokens: list) -> str:
    for intent, kws in _KEYWORD_MAP.items():
        if any(t in kws for t in tokens):
            return intent
    return "unknown"


def classify_intent(tokens: list) -> str:
    """
    Classify the intent using ML (TF-IDF + Logistic Regression).
    Falls back to keyword matching if ML confidence < threshold.
    """
    query_text = " ".join(tokens)
    if not query_text.strip():
        return _keyword_fallback(tokens)

    query_vec   = _vec.transform([query_text])
    proba       = _clf.predict_proba(query_vec)[0]
    best_idx    = proba.argmax()
    confidence  = proba[best_idx]

    if confidence >= _ML_CONFIDENCE_THRESHOLD:
        return _clf.classes_[best_idx]
    return _keyword_fallback(tokens)
