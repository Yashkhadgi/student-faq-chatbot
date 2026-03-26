# M-10: Analytics Logger — CSV + summary stats
import csv
import os
from datetime import datetime
from collections import Counter
from config import ANALYTICS_LOG


def log_event(query: str, intent: str, entities: dict, score: float,
              status: str, session_id: str = "") -> None:
    """Append one interaction row to logs.csv."""
    file_exists = os.path.isfile(ANALYTICS_LOG)
    with open(ANALYTICS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "query", "intent", "score", "response", "session_id"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            query,
            intent,
            round(score, 4),
            status,
            session_id,
        ])


def get_recent_logs(limit: int = 50) -> list[dict]:
    """Return the last `limit` log rows as a list of dicts."""
    if not os.path.isfile(ANALYTICS_LOG):
        return []
    rows: list[dict] = []
    try:
        with open(ANALYTICS_LOG, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    except Exception:
        return []
    return rows[-limit:]


def get_analytics_summary() -> dict:
    """
    Compute aggregate stats over all logs.

    Returns:
        total_queries, most_common_intent, avg_confidence, fallback_rate,
        intent_distribution (dict)
    """
    logs = get_recent_logs(limit=10_000)
    if not logs:
        return {
            "total_queries":     0,
            "most_common_intent": "N/A",
            "avg_confidence":    0.0,
            "fallback_rate":     0.0,
            "intent_distribution": {},
        }

    intents   = [r.get("intent", "unknown") for r in logs]
    scores    = []
    fallbacks = 0
    for r in logs:
        try:
            scores.append(float(r.get("score", 0)))
        except ValueError:
            pass
        if r.get("response") == "fallback":
            fallbacks += 1

    intent_counts = Counter(intents)
    most_common   = intent_counts.most_common(1)[0][0] if intent_counts else "N/A"

    return {
        "total_queries":      len(logs),
        "most_common_intent": most_common,
        "avg_confidence":     round(sum(scores) / len(scores), 4) if scores else 0.0,
        "fallback_rate":      round(fallbacks / len(logs) * 100, 2) if logs else 0.0,
        "intent_distribution": dict(intent_counts),
    }
