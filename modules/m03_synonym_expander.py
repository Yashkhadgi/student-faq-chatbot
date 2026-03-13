# M-03: Synonym Expander
# Owner: Team Leader
from utils.helpers import load_synonyms

def expand_synonyms(tokens: list) -> list:
    synonyms = load_synonyms()
    expanded = list(tokens)
    for token in tokens:
        if token in synonyms:
            expanded.extend(synonyms[token])
    seen = set()
    result = []
    for word in expanded:
        if word not in seen:
            seen.add(word)
            result.append(word)
    return result
