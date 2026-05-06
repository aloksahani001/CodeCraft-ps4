"""
Data Loader — Issues 1-4
Loads all CSVs into fast O(1) dict structures.
"""
import csv
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"

PLATFORMS = ["Instagram", "YouTube"]
CONTENT_TYPES = ["SHORT", "LONG"]


def load_creators(path=None):
    """Returns {creator_id(int): {"base_engagement": float, "cooldown_hours": int}}"""
    path = path or DATA_DIR / "creators.csv"
    creators = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = int(row["creator_id"])
            creators[cid] = {
                "base_engagement": float(row["base_engagement"]),
                "cooldown_hours": int(row["cooldown_hours"]),
            }
    return creators


def load_content(path=None):
    """Returns list of content dicts, sorted by content_id."""
    path = path or DATA_DIR / "content.csv"
    items = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            items.append({
                "content_id": int(row["content_id"]),
                "creator_id": int(row["creator_id"]),
                "content_type": row["content_type"].strip().upper(),
                "created_timestamp": int(row["created_timestamp"]),
                "time_sensitivity": row["time_sensitivity"].strip(),
            })
    items.sort(key=lambda x: x["content_id"])
    return items


def load_platform_activity(path=None):
    """Returns {(platform, time_slot): activity_score}"""
    path = path or DATA_DIR / "platform_activity.csv"
    activity = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (row["platform"].strip(), int(row["time_slot"]))
            activity[key] = float(row["activity_score"])
    return activity


def load_historical_engagement(path=None):
    """Returns {(creator_id, platform, content_type, time_slot): avg_engagement}"""
    path = path or DATA_DIR / "historical_engagement.csv"
    hist = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = (
                int(row["creator_id"]),
                row["platform"].strip(),
                row["content_type"].strip().upper(),
                int(row["time_slot"]),
            )
            hist[key] = float(row["avg_engagement"])
    return hist


def build_creator_avg_engagement(hist):
    """Pre-compute per-creator average engagement for fallback."""
    totals = {}
    counts = {}
    for (cid, plat, ctype, slot), val in hist.items():
        totals[cid] = totals.get(cid, 0.0) + val
        counts[cid] = counts.get(cid, 0) + 1
    return {cid: totals[cid] / counts[cid] for cid in totals}


def load_all():
    """Load all datasets and return as a single context dict."""
    creators = load_creators()
    content = load_content()
    platform_activity = load_platform_activity()
    hist = load_historical_engagement()
    creator_avg = build_creator_avg_engagement(hist)
    global_avg = sum(hist.values()) / len(hist) if hist else 0.5
    return {
        "creators": creators,
        "content": content,
        "platform_activity": platform_activity,
        "historical_engagement": hist,
        "creator_avg_engagement": creator_avg,
        "global_avg_engagement": global_avg,
    }