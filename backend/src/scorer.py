"""
Scorer — Issues 5, 8, 17
Computes engagement score for a (content_item, platform, time_slot) triple.
score = platform_activity × historical_engagement × base_engagement
"""

PLATFORMS = ["Instagram", "YouTube"]
TIME_SLOTS = list(range(24))


def get_historical_engagement(content_item, platform, time_slot, ctx):
    """
    Look up historical engagement with fallback chain:
      1. Exact (creator, platform, content_type, slot)
      2. Creator average across all conditions
      3. Global average
    """
    hist = ctx["historical_engagement"]
    creator_avg = ctx["creator_avg_engagement"]
    global_avg = ctx["global_avg_engagement"]

    key = (
        content_item["creator_id"],
        platform,
        content_item["content_type"],
        time_slot,
    )
    if key in hist:
        return hist[key]

    # Fallback: creator average
    cid = content_item["creator_id"]
    if cid in creator_avg:
        return creator_avg[cid]

    return global_avg


def score(content_item, platform, time_slot, ctx):
    """
    Compute engagement score for a given platform + time_slot combo.
    Returns float >= 0.
    """
    activity = ctx["platform_activity"].get((platform, time_slot), 0.6)
    hist_eng = get_historical_engagement(content_item, platform, time_slot, ctx)
    creators = ctx["creators"]

    cid = content_item["creator_id"]
    base_eng = creators[cid]["base_engagement"] if cid in creators else 1.0

    # Edge-case: zero activity still valid (low but not error)
    raw = activity * hist_eng * base_eng
    return max(raw, 0.0)


def score_all_combos(content_item, ctx):
    """
    Evaluate all (platform × time_slot) combinations.
    Returns list of (score, platform, time_slot) sorted descending by score,
    then ascending by platform (alpha), then ascending by time_slot — deterministic.
    """
    results = []
    for platform in PLATFORMS:
        for slot in TIME_SLOTS:
            s = score(content_item, platform, slot, ctx)
            results.append((s, platform, slot))

    # Deterministic sort: highest score first, ties broken by platform alpha then slot
    results.sort(key=lambda x: (-x[0], x[1], x[2]))
    return results
