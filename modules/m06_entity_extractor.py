# M-06: Entity Extractor
# Owner: Member B
import re

def extract_entities(raw_query: str) -> dict:
    entities = {"course": [], "date": [], "dept": []}
    courses = re.findall(r'[A-Z]{2,}-\d{3}', raw_query.upper())
    entities["course"] = courses
    dates = re.findall(r'\d{1,2}(?:st|nd|rd|th)?\s+\w+|\w+\s+\d{4}', raw_query)
    entities["date"] = dates
    return entities
