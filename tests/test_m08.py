"""Tests for M08 — Fallback Handler"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m08_fallback_handler import handle_fallback


def test_empty_candidates_returns_clarify():
    result = handle_fallback("some random query", [])
    assert isinstance(result, str)
    assert len(result) > 0


def test_low_score_candidates_triggers_escalation():
    candidates = [{"question": "What is the fee?", "score": 0.01}]
    result = handle_fallback("random xyz", candidates)
    assert isinstance(result, str)


def test_suggestion_included_for_weak_candidates():
    candidates = [
        {"question": "What is the fee?", "score": 0.10},
        {"question": "How to apply?",    "score": 0.07},
    ]
    result = handle_fallback("something vague", candidates)
    # Should contain at least one suggested question
    assert "What is the fee?" in result or "How to apply?" in result


def test_escalation_contains_sit_contact():
    # Candidates with score=0.0 won't trigger suggestions path → goes to FALLBACK_ESCALATE
    candidates = [{"question": "What is fee?", "score": 0.0}]
    result = handle_fallback("totally unrelated query", candidates)
    # The escalation message should reference SIT contact info
    assert "sitng" in result.lower() or "helpdesk" in result.lower() or "wa.me" in result.lower()


def test_returns_string_always():
    for candidates in [[], [{"question": "Q?", "score": 0.0}]]:
        result = handle_fallback("test", candidates)
        assert isinstance(result, str)


def test_no_suggestion_for_zero_score():
    candidates = [{"question": "What is fee?", "score": 0.0}]
    result = handle_fallback("random", candidates)
    # Score=0.0 should NOT trigger suggestion; should escalate
    assert "What is fee?" not in result
