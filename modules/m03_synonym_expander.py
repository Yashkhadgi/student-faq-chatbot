# M-03: Synonym Expander
# Owner: Team Leader
# Purpose: Expand query tokens using synonyms.json so TF-IDF finds
#          more matches even when student uses different words.
# Example: "fee" → ["fee", "tuition", "charges", "cost", "payment"]

from utils.helpers import load_synonyms

def expand_synonyms(tokens: list) -> list:
    """
    Takes a list of tokens, expands each one using the
    synonym dictionary, returns a deduplicated expanded list.
    """
    synonyms = load_synonyms()
    expanded = list(tokens)  # start with original tokens

    for token in tokens:
        if token in synonyms:
            expanded.extend(synonyms[token])  # add all synonyms

    # Remove duplicates but keep order
    seen = set()
    result = []
    for word in expanded:
        if word not in seen:
            seen.add(word)
            result.append(word)

    return result
