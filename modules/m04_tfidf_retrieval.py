# M-04: TF-IDF Retrieval — vectorizer fitted ONCE at module load
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.helpers import load_faqs
from config import TFIDF_TOP_N

# ── Fit vectorizer once on all FAQ questions + tags ───────────────────────────
_faqs   = load_faqs()
_corpus = [faq["question"] + " " + " ".join(faq.get("tags", [])) for faq in _faqs]
_vectorizer   = TfidfVectorizer()
_faq_matrix   = _vectorizer.fit_transform(_corpus)   # shape: (n_faqs, vocab)


def retrieve(tokens: list) -> list:
    """
    Transform the query tokens against the pre-fitted vectorizer.
    Returns top-N FAQs with cosine similarity scores.
    """
    query_string  = " ".join(tokens)
    query_vector  = _vectorizer.transform([query_string])   # transform only — no refit
    scores        = cosine_similarity(query_vector, _faq_matrix).flatten()
    top_indices   = scores.argsort()[::-1][:TFIDF_TOP_N]

    results = []
    for i in top_indices:
        results.append({
            "id":       _faqs[i]["id"],
            "question": _faqs[i]["question"],
            "answer":   _faqs[i]["answer"],
            "intent":   _faqs[i].get("intent", "unknown"),
            "score":    round(float(scores[i]), 4)
        })
    return results
