"""
Output Formatter + Validator — Issues 12, 16
Produces clean CSV output and validates field constraints.
"""

import csv
import io

VALID_PLATFORMS = {"Instagram", "YouTube"}
VALID_DECISIONS = {"POST_NOW", "SCHEDULE"}
OUTPUT_FIELDS = ["content_id", "platform", "time_slot", "decision"]


def validate_recommendation(rec):
    """
    Validate a single recommendation dict.
    Raises ValueError with descriptive message on failure.
    """
    if rec["platform"] not in VALID_PLATFORMS:
        raise ValueError(f"content_id={rec['content_id']}: invalid platform '{rec['platform']}'")
    if rec["decision"] not in VALID_DECISIONS:
        raise ValueError(f"content_id={rec['content_id']}: invalid decision '{rec['decision']}'")
    slot = rec["time_slot"]
    if not (0 <= slot <= 23):
        raise ValueError(f"content_id={rec['content_id']}: time_slot {slot} out of range 0–23")
    if not isinstance(rec["content_id"], int):
        raise ValueError(f"content_id must be int, got {type(rec['content_id'])}")
    return True


def validate_all(recommendations):
    """Validate all recommendations. Returns (valid_list, errors_list)."""
    valid, errors = [], []
    for rec in recommendations:
        try:
            validate_recommendation(rec)
            valid.append(rec)
        except ValueError as e:
            errors.append(str(e))
    return valid, errors


def to_csv_string(recommendations):
    """Serialize recommendations to CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=OUTPUT_FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(recommendations)
    return buf.getvalue()


def write_csv(recommendations, path):
    """Write recommendations to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(recommendations)
    return path


def print_table(recommendations, max_rows=None):
    """Pretty-print recommendations as a table."""
    rows = recommendations[:max_rows] if max_rows else recommendations
    header = f"{'content_id':>12} {'platform':>12} {'time_slot':>10} {'decision':>12}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['content_id']:>12} {r['platform']:>12} {r['time_slot']:>10} {r['decision']:>12}")
    if max_rows and len(recommendations) > max_rows:
        print(f"  ... and {len(recommendations) - max_rows} more rows")