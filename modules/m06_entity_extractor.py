# M-06: Entity Extractor — courses, dates, semesters, departments
import re

# Ordinal words → number mapping for semester detection
_ORDINAL_MAP = {
    "first": "1", "second": "2", "third": "3", "fourth": "4",
    "fifth": "5", "sixth": "6", "seventh": "7", "eighth": "8",
    "1st": "1", "2nd": "2", "3rd": "3", "4th": "4",
    "5th": "5", "6th": "6", "7th": "7", "8th": "8",
}

# Known SIT Nagpur departments
_DEPT_PATTERNS = {
    "CS":          r"\bcs\b|\bcomputer science\b|\bcomp sci\b",
    "IT":          r"\bit\b|\binformation technology\b",
    "ENTC":        r"\bentc\b|\belectronics\b|\belectronics and telecom\b",
    "Mechanical":  r"\bmech\b|\bmechanical\b",
    "Civil":       r"\bcivil\b",
    "AIDS":        r"\baids\b|\bartificial intelligence\b|\bai\b|\bdata science\b",
}


def extract_entities(raw_query: str) -> dict:
    """
    Extract structured entities from the raw query.

    Returns:
        dict with keys:
            "course"   — list of course codes like ["CS-301", "IT-204"]
            "date"     — list of date strings
            "semester" — list of semester numbers as strings ["3", "5"]
            "dept"     — list of department names ["CS", "IT"]
    """
    entities: dict[str, list] = {
        "course":   [],
        "date":     [],
        "semester": [],
        "dept":     [],
    }
    q_lower = raw_query.lower()

    # ── Course codes: CS-301, IT-204, ENTC-501, etc. ─────────────────────────
    courses = re.findall(r"\b[A-Za-z]{2,5}-\d{3}\b", raw_query)
    entities["course"] = [c.upper() for c in courses]

    # ── Dates: "15th November", "June 2025", "31st August" ───────────────────
    dates = re.findall(
        r"\d{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
        r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"|\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
        r"dec(?:ember)?)\s+\d{4}",
        raw_query,
        flags=re.IGNORECASE
    )
    entities["date"] = dates

    # ── Semester numbers: "sem 3", "semester 5", "third sem", "5th semester" ──
    sems: list[str] = []

    # Pattern 1: "sem 3", "semester 3", "sem-3"
    for m in re.finditer(r"\bsem(?:ester)?[\s\-]*(\d)\b", q_lower):
        sems.append(m.group(1))

    # Pattern 2: "third semester", "5th sem"
    for word, num in _ORDINAL_MAP.items():
        pattern = rf"\b{re.escape(word)}\s+sem(?:ester)?\b"
        if re.search(pattern, q_lower):
            sems.append(num)

    entities["semester"] = list(dict.fromkeys(sems))   # deduplicate, preserve order

    # ── Department names ──────────────────────────────────────────────────────
    depts: list[str] = []
    for dept_name, pattern in _DEPT_PATTERNS.items():
        if re.search(pattern, q_lower):
            depts.append(dept_name)
    entities["dept"] = depts

    return entities


def enrich_answer_with_entities(answer: str, entities: dict) -> str:
    """
    Optionally prepend entity context to the answer for specificity.
    E.g., "For SEM 5 (CS): The BTech fee is..."
    """
    prefix_parts = []
    if entities.get("semester"):
        prefix_parts.append(f"SEM {', '.join(entities['semester'])}")
    if entities.get("dept"):
        prefix_parts.append(f"{', '.join(entities['dept'])}")
    if entities.get("course"):
        prefix_parts.append(f"Course {', '.join(entities['course'])}")

    if prefix_parts:
        prefix = "For " + " — ".join(prefix_parts) + ": "
        return prefix + answer
    return answer
