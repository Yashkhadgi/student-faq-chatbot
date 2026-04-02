# M-02: Query Preprocessor — full NLP pipeline
import re
import string

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus   import stopwords

# Domain-specific words we NEVER remove, even if they are stopwords
_DOMAIN_KEEP = {
    "fee", "fees", "exam", "exams", "hostel", "admission", "admissions",
    "scholarship", "attendance", "result", "results", "library", "contact",
    "schedule", "timetable", "semester", "sem", "date", "deadline", "document",
    "documents", "marks", "grades", "portal", "apply", "application",
    "btech", "mtech", "mba", "cgpa", "sgpa", "noc", "tc", "lc", "obc", "scst", "ews"
}

# Download required NLTK data quietly (no-op if already present)
for _pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.data.find(f"tokenizers/{_pkg}" if "punkt" in _pkg else f"corpora/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True)

_STOPWORDS_SET: set[str] = set(stopwords.words("english")) - _DOMAIN_KEEP


def _normalize_spelling(text: str) -> str:
    """Basic spelling correction using TextBlob (optional — falls back gracefully)."""
    try:
        from textblob import TextBlob
        return str(TextBlob(text).correct())
    except Exception:
        return text


def preprocess(raw_query: str, correct_spelling: bool = False) -> dict:
    """
    Full preprocessing pipeline.

    Steps:
      1. Lowercase
      2. Optional spelling correction (TextBlob)
      3. Punctuation removal
      4. NLTK word tokenization
      5. Stopword removal (preserving domain words)

    Returns:
        dict with keys:
            "tokens"  — cleaned token list
            "cleaned" — cleaned string (space-joined tokens)
    """
    text = raw_query.lower().strip()

    if correct_spelling:
        text = _normalize_spelling(text)

    # Remove punctuation except hyphens inside course codes like CS-301
    text = re.sub(r"(?<!\w)-(?!\w)", " ", text)            # isolated hyphens → space
    text = text.translate(str.maketrans("", "", string.punctuation.replace("-", "")))

    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t.isalpha() or re.match(r"[a-z]+-\d+", t)]  # keep course codes
    tokens = [t for t in tokens if t not in _STOPWORDS_SET or t in _DOMAIN_KEEP]

    return {
        "tokens":  tokens,
        "cleaned": " ".join(tokens)
    }
