"""Tests for M02 — Text Preprocessor"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m02_preprocessor import preprocess


def test_returns_dict_with_tokens_and_cleaned():
    result = preprocess("What is the fee?", correct_spelling=False)
    assert isinstance(result, dict)
    assert "tokens" in result
    assert "cleaned" in result


def test_lowercase_conversion():
    result = preprocess("WHAT IS THE FEE?", correct_spelling=False)
    for token in result["tokens"]:
        assert token == token.lower()


def test_punctuation_removed():
    result = preprocess("fees, exams! library?", correct_spelling=False)
    cleaned = result["cleaned"]
    for punc in [",", "!", "?"]:
        assert punc not in cleaned


def test_stopwords_removed_but_domain_words_kept():
    result = preprocess("What are the fees for the exam", correct_spelling=False)
    tokens = result["tokens"]
    # Domain words should survive
    assert "fees" in tokens or "fee" in tokens or "exam" in tokens
    # Common stopwords without domain meaning should be removed
    assert "the" not in tokens
    assert "are" not in tokens


def test_empty_string_returns_empty_tokens():
    result = preprocess("", correct_spelling=False)
    assert result["tokens"] == []
    assert result["cleaned"] == ""


def test_course_code_preserved():
    result = preprocess("Tell me about CS-301 timetable", correct_spelling=False)
    tokens = result["tokens"]
    # 'cs' should be in tokens even if course code is split
    assert any("cs" in t.lower() for t in tokens)
