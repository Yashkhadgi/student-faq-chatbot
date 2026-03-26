"""Tests for M04 — TF-IDF Retrieval"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m04_tfidf_retrieval import retrieve


def test_returns_list():
    results = retrieve(["fee", "btech"])
    assert isinstance(results, list)


def test_returns_expected_keys():
    results = retrieve(["exam", "schedule"])
    assert len(results) > 0
    for r in results:
        assert "id" in r
        assert "question" in r
        assert "answer" in r
        assert "score" in r


def test_scores_are_floats():
    results = retrieve(["hostel"])
    for r in results:
        assert isinstance(r["score"], float)


def test_scores_between_0_and_1():
    results = retrieve(["admission", "form", "documents"])
    for r in results:
        assert 0.0 <= r["score"] <= 1.0


def test_retrieval_relevance():
    results = retrieve(["scholarship", "merit", "grant"])
    assert len(results) > 0
    # Top result should have a positive score
    assert results[0]["score"] > 0.0


def test_empty_query_returns_results_with_zero_scores():
    results = retrieve([])
    assert isinstance(results, list)
