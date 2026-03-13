# M-04: TF-IDF Retrieval
# Owner: Team Leader
# Purpose: Vectorize the expanded query and compare against all FAQs
#          using cosine similarity. Returns top-N ranked matches.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.helpers import load_faqs
from config import TFIDF_TOP_N

def retrieve(tokens: list) -> list:
    """
    Takes expanded tokens, finds top-N matching FAQs using TF-IDF.
    Returns list of dicts sorted by score descending:
    [{ "id", "question", "answer", "score" }, ...]
    """
    faqs = load_faqs()

    # Build corpus — one string per FAQ (question + tags joined)
    corpus = []
    for faq in faqs:
        tags = " ".join(faq.get("tags", []))
        corpus.append(faq["question"] + " " + tags)

    # Convert query tokens back to a single string
    query_string = " ".join(tokens)

    # Fit TF-IDF on corpus + query together
    vectorizer = TfidfVectorizer()
    all_docs = corpus + [query_string]
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    # Query vector is the last row
    query_vector = tfidf_matrix[-1]
    faq_vectors  = tfidf_matrix[:-1]

    # Compute cosine similarity between query and all FAQs
    scores = cosine_similarity(query_vector, faq_vectors).flatten()

    # Get top-N indices sorted by score
    top_indices = scores.argsort()[::-1][:TFIDF_TOP_N]

    results = []
    for i in top_indices:
        results.append({
            "id":       faqs[i]["id"],
            "question": faqs[i]["question"],
            "answer":   faqs[i]["answer"],
            "score":    round(float(scores[i]), 4)
        })

    return results
