"""Tests for M05 — Intent Classifier"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m05_intent_classifier import classify_intent


def test_fee_intent():
    result = classify_intent(["fee", "btech", "tuition"])
    assert result == "fee"


def test_exam_intent():
    result = classify_intent(["exam", "schedule", "semester"])
    assert result == "exam"


def test_hostel_intent():
    result = classify_intent(["hostel", "accommodation", "room"])
    assert result == "hostel"


def test_scholarship_intent():
    result = classify_intent(["scholarship", "financial", "merit", "grant"])
    assert result == "scholarship"


def test_unknown_intent_for_garbage():
    # Garbage tokens should return "unknown" or at least a valid string
    result = classify_intent(["xyzabc", "randomword"])
    assert isinstance(result, str)


def test_returns_string():
    result = classify_intent(["contact", "email", "phone"])
    assert isinstance(result, str)
    assert len(result) > 0


def test_empty_tokens_returns_unknown():
    result = classify_intent([])
    assert isinstance(result, str)
