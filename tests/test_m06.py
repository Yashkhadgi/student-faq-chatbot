"""Tests for M06 — Entity Extractor"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.m06_entity_extractor import extract_entities, enrich_answer_with_entities


def test_returns_expected_keys():
    entities = extract_entities("What is CS-301?")
    assert "course" in entities
    assert "date" in entities
    assert "semester" in entities
    assert "dept" in entities


def test_course_code_extracted():
    entities = extract_entities("Tell me about CS-301 and IT-204")
    assert "CS-301" in entities["course"]
    assert "IT-204" in entities["course"]


def test_semester_number_extracted():
    entities = extract_entities("What are the fees for sem 5?")
    assert "5" in entities["semester"]


def test_ordinal_semester_extracted():
    entities = extract_entities("I am in third semester")
    assert "3" in entities["semester"]


def test_department_extracted():
    entities = extract_entities("What is the CS timetable?")
    assert "CS" in entities["dept"]


def test_no_entities_empty_query():
    entities = extract_entities("")
    assert entities["course"] == []
    assert entities["semester"] == []
    assert entities["dept"] == []


def test_enrich_answer_prepends_context():
    entities = {"semester": ["5"], "dept": ["CS"], "course": [], "date": []}
    base = "The fee is Rs. 1,20,000."
    enriched = enrich_answer_with_entities(base, entities)
    assert "SEM 5" in enriched
    assert "CS" in enriched
    assert base in enriched


def test_enrich_empty_entities_returns_base():
    entities = {"semester": [], "dept": [], "course": [], "date": []}
    base = "The fee is Rs. 1,20,000."
    assert enrich_answer_with_entities(base, entities) == base
