# M-10: Analytics Logger
# Owner: Member C
import csv
import os
from datetime import datetime
from config import ANALYTICS_LOG

def log_event(query: str, intent: str, entities: dict, score: float, status: str):
    file_exists = os.path.isfile(ANALYTICS_LOG)
    with open(ANALYTICS_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp","query","intent","entities","confidence_score","status"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            query, intent, str(entities), round(score, 4), status
        ])
