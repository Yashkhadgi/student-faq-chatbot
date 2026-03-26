"""Tests for M03 — Synonym Expander"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m03_synonym_expander import expand_synonyms


def test_expands_known_synonym():
    tokens = ["fee"]
    result = expand_synonyms(tokens)
    # "tuition" and "cost" should be in the synonyms for "fee"
    assert "tuition" in result or "cost" in result


def test_original_tokens_preserved():
    tokens = ["fee", "hostel"]
    result = expand_synonyms(tokens)
    assert "fee" in result
    assert "hostel" in result


def test_no_duplicates_in_result():
    tokens = ["exam", "test"]   # "test" is a synonym of "exam"
    result = expand_synonyms(tokens)
    assert len(result) == len(set(result)), "Duplicates found in expanded list"


def test_unknown_token_passed_through():
    tokens = ["xyzabc123"]
    result = expand_synonyms(tokens)
    assert "xyzabc123" in result


def test_empty_tokens():
    assert expand_synonyms([]) == []


def test_multiple_synonyms_expanded():
    tokens = ["scholarship"]
    result = expand_synonyms(tokens)
    assert len(result) > 1   # should expand to at least one synonym
