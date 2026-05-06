"""
Tests — Issue 20
Run from repo root: python tests/test_system.py
"""
import sys
from pathlib import Path

# Add backend/ to path so `from src.x import y` works
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.data_loader import load_all
from src.scorer import score, score_all_combos
from src.recommender import recommend, recommend_all
from src.output_formatter import validate_all, to_csv_string


def make_ctx():
    return load_all()


def test_data_loading():
    ctx = make_ctx()
    assert len(ctx["creators"]) == 50, "Expected 50 creators"
    assert len(ctx["content"]) == 100, "Expected 100 content items"
    assert len(ctx["platform_activity"]) == 48, "Expected 48 platform-slot entries (2×24)"
    assert len(ctx["historical_engagement"]) == 4800, f"Expected 4800 hist rows, got {len(ctx['historical_engagement'])}"
    print("✓ Data loading: all 4 datasets loaded correctly")


def test_score_positive():
    ctx = make_ctx()
    item = ctx["content"][0]
    s = score(item, "Instagram", 18, ctx)
    assert s > 0, f"Score should be positive, got {s}"
    print(f"✓ Score positive: {s:.4f}")


def test_score_all_combos_length():
    ctx = make_ctx()
    item = ctx["content"][0]
    combos = score_all_combos(item, ctx)
    assert len(combos) == 48, f"Expected 48 combos, got {len(combos)}"
    scores = [c[0] for c in combos]
    assert scores[0] >= scores[-1], "Combos should be sorted descending"
    print("✓ score_all_combos: 48 entries, sorted descending")


def test_determinism():
    ctx = make_ctx()
    item = ctx["content"][5]
    r1 = recommend(item, ctx)
    r2 = recommend(item, ctx)
    assert r1 == r2, "Recommendations must be deterministic"
    print("✓ Determinism: same input → same output")


def test_output_validity():
    ctx = make_ctx()
    recs = recommend_all(ctx)
    valid, errors = validate_all(recs)
    assert len(errors) == 0, f"Validation errors: {errors}"
    assert len(valid) == 100, f"Expected 100 recs, got {len(valid)}"
    print("✓ All 100 recommendations pass validation")


def test_output_fields():
    ctx = make_ctx()
    recs = recommend_all(ctx)
    for r in recs:
        assert r["platform"] in {"Instagram", "YouTube"}, f"Bad platform: {r['platform']}"
        assert r["decision"] in {"POST_NOW", "SCHEDULE"}, f"Bad decision: {r['decision']}"
        assert 0 <= r["time_slot"] <= 23, f"Slot out of range: {r['time_slot']}"
    print("✓ Output fields: platform, decision, time_slot all valid")


def test_missing_creator_fallback():
    ctx = make_ctx()
    fake_item = {
        "content_id": 9999,
        "creator_id": 9999,  # unknown creator
        "content_type": "SHORT",
        "created_timestamp": 10,
        "time_sensitivity": "Medium",
    }
    s = score(fake_item, "Instagram", 10, ctx)
    assert s >= 0, f"Score should be non-negative even for unknown creator, got {s}"
    print(f"✓ Missing creator fallback: score={s:.4f} (no crash)")


def test_post_now_logic():
    ctx = make_ctx()
    # Any item where created_timestamp == time_slot should be POST_NOW
    recs = recommend_all(ctx)
    content_map = {item["content_id"]: item for item in ctx["content"]}
    for rec in recs:
        item = content_map[rec["content_id"]]
        if rec["decision"] == "POST_NOW":
            assert rec["time_slot"] == item["created_timestamp"], (
                f"POST_NOW but slots differ: content_id={rec['content_id']}, "
                f"created={item['created_timestamp']}, recommended={rec['time_slot']}"
            )
    print("✓ POST_NOW logic: all POST_NOW recs have slot == created_timestamp")


def test_csv_output_format():
    ctx = make_ctx()
    recs = recommend_all(ctx)
    csv_str = to_csv_string(recs)
    lines = csv_str.strip().split("\n")
    assert lines[0] == "content_id,platform,time_slot,decision", f"Bad header: {lines[0]}"
    assert len(lines) == 101, f"Expected 101 lines (header + 100), got {len(lines)}"
    # Check no internal fields leaked
    assert "_best_score" not in lines[0]
    print("✓ CSV format: correct header, 100 data rows, no internal fields")


def test_peak_hour_preference():
    """Verify recommendations prefer peak hours (Instagram 18-22, YouTube 20-23)."""
    ctx = make_ctx()
    recs = recommend_all(ctx)
    PEAKS = {"Instagram": set(range(18, 23)), "YouTube": set(range(20, 24))}
    peak_hits = sum(
        1 for r in recs if r["time_slot"] in PEAKS.get(r["platform"], set())
    )
    ratio = peak_hits / len(recs)
    assert ratio >= 0.90, f"Expected ≥90% peak-hour recs, got {ratio:.0%}"
    print(f"✓ Peak hour preference: {ratio:.0%} of recs land in peak hours")


if __name__ == "__main__":
    tests = [
        test_data_loading,
        test_score_positive,
        test_score_all_combos_length,
        test_determinism,
        test_output_validity,
        test_output_fields,
        test_missing_creator_fallback,
        test_post_now_logic,
        test_csv_output_format,
        test_peak_hour_preference,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"✗ {t.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")
