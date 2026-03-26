"""Tests for M01 — Basic FAQ Responder"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m01_basic_faq import basic_faq_lookup


def test_known_query_returns_result():
    result = basic_faq_lookup("What is the fee for btech?")
    assert result is not None
    assert "faq" in result
    assert "score" in result


def test_score_is_positive_for_match():
    result = basic_faq_lookup("hostel accommodation available")
    assert result is not None
    assert result["score"] > 0.0


def test_high_confidence_admission_query():
    result = basic_faq_lookup("last date for admission form")
    assert result is not None
    assert result["score"] >= 0.2


def test_exam_query_returns_faq():
    result = basic_faq_lookup("When are semester exams scheduled?")
    assert result is not None
    faq = result["faq"]
    assert "exam" in faq["intent"] or "exam" in [t.lower() for t in faq.get("tags", [])]


def test_completely_unrelated_query_score_near_zero():
    result = basic_faq_lookup("xyz abc random nonsense 12345")
    # Should return something (best effort), but score should be very low or None
    if result is not None:
        assert result["score"] < 0.5


def test_scholarship_query():
    result = basic_faq_lookup("How do I apply for a scholarship?")
    assert result is not None
    assert result["faq"]["intent"] == "scholarship"
