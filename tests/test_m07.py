"""Tests for M07 — Context Manager"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m07_context_manager import enrich_with_context, update_context


def test_enrich_returns_expected_keys():
    session = {"history": []}
    result  = enrich_with_context("What is the fee?", ["fee", "btech"], session)
    assert "raw_query" in result
    assert "tokens" in result
    assert "is_followup" in result


def test_non_followup_detection():
    session = {"history": []}
    result  = enrich_with_context("What is the hostel fee?", ["hostel", "fee"], session)
    assert result["is_followup"] == False


def test_followup_detection():
    session = {"history": [{"query": "fees?", "answer": "...", "intent": "fee", "entities": {}}]}
    result  = enrich_with_context("What about that?", ["what", "about", "that"], session)
    assert result["is_followup"] == True


def test_context_enriched_with_last_intent():
    session = {"history": [{"query": "fees?", "answer": "...", "intent": "fee", "entities": {}}]}
    result  = enrich_with_context("Tell me more", ["tell", "more"], session)
    assert "fee" in result["tokens"]


def test_update_context_adds_turn():
    session = {"history": []}
    update_context(session, "fees?", "Rs 1,20,000", "fee", {})
    assert len(session["history"]) == 1
    assert session["history"][0]["intent"] == "fee"


def test_context_window_respected():
    session = {"history": []}
    for i in range(5):
        update_context(session, f"query {i}", f"answer {i}", "fee", {})
    # CONTEXT_WINDOW is 3 — only last 3 should be kept
    assert len(session["history"]) <= 3
