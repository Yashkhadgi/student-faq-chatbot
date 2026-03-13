# M-02: Query Preprocessor
# Owner: Member B
import re

def preprocess(raw_query: str) -> list:
    query = raw_query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    tokens = query.split()
    return tokens
