#!/usr/bin/env python3
"""
Creator Content Posting Optimization System
Run from repo root:  python backend/main.py
Or from backend/:    python main.py
Output: output/submission.csv
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import load_all
from src.recommender import recommend_all
from src.output_formatter import validate_all, write_csv, print_table
from src.evaluator import compute_metrics, print_metrics

OUTPUT_PATH = Path(__file__).parent.parent / "output" / "submission.csv"


def main():
    t0 = time.perf_counter()

    print("Loading data...")
    ctx = load_all()
    print(f"  Creators:                  {len(ctx['creators'])}")
    print(f"  Content items:             {len(ctx['content'])}")
    print(f"  Platform activity entries: {len(ctx['platform_activity'])}")
    print(f"  Historical engagement rows:{len(ctx['historical_engagement'])}")

    print("\nGenerating recommendations...")
    recommendations = recommend_all(ctx)

    latency = time.perf_counter() - t0

    print("\nValidating output...")
    valid, errors = validate_all(recommendations)
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    {e}")
    else:
        print(f"  All {len(valid)} recommendations valid.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_csv(valid, OUTPUT_PATH)
    print(f"\nOutput written to: {OUTPUT_PATH}")

    print("\nSample output (first 10 rows):")
    print_table(valid, max_rows=10)

    metrics = compute_metrics(recommendations, ctx, latency_seconds=latency)
    print_metrics(metrics)

    print(f"\nTotal runtime: {latency*1000:.1f} ms")


if __name__ == "__main__":
    main()