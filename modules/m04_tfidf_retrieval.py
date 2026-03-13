# M-04: TF-IDF Retrieval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.helpers import load_faqs
from config import TFIDF_TOP_N

def retrieve(tokens: list) -> list:
    faqs = load_faqs()
    corpus = []
    for faq in faqs:
        tags = " ".join(faq.get("tags", []))
        corpus.append(faq["question"] + " " + tags)
    query_string = " ".join(tokens)
    vectorizer = TfidfVectorizer()
    all_docs = corpus + [query_string]
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    query_vector = tfidf_matrix[-1]
    faq_vectors  = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vector, faq_vectors).flatten()
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
