# M-07 | Owner: Member C
def enrich_with_context(raw_query: str, tokens: list, session: dict) -> dict:
    raise NotImplementedError("Member C: implement context enrichment")

def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    raise NotImplementedError("Member C: implement context update")
