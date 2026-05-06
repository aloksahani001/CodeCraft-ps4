"""
Recommender — Issues 6, 7, 8, 9, 10, 11
Jointly optimizes platform + time_slot, then decides POST_NOW vs SCHEDULE.
Fully deterministic.
"""

from .scorer import score, score_all_combos

DECISION_POST_NOW = "POST_NOW"
DECISION_SCHEDULE = "SCHEDULE"


def recommend(content_item, ctx):
    """
    Generate a recommendation for a single content item.

    Returns dict:
      content_id, platform, recommended_time_slot, decision
    """
    # Joint optimization: rank all 48 (platform, slot) combos
    ranked = score_all_combos(content_item, ctx)

    # Best combo — deterministic due to sort in score_all_combos
    best_score, best_platform, best_slot = ranked[0]

    # Scheduling decision:
    # Score at the submission timestamp on the best platform
    current_slot = content_item["created_timestamp"]
    current_score = score(content_item, best_platform, current_slot, ctx)

    # POST_NOW if current slot IS the best slot, or scores are equal (prefer immediacy)
    if current_slot == best_slot or current_score >= best_score:
        decision = DECISION_POST_NOW
        recommended_slot = current_slot
    else:
        decision = DECISION_SCHEDULE
        recommended_slot = best_slot

    return {
        "content_id": content_item["content_id"],
        "platform": best_platform,
        "time_slot": recommended_slot,
        "decision": decision,
        "_best_score": best_score,
        "_current_score": current_score,
    }


def recommend_all(ctx):
    """Process all content items. Returns list of recommendation dicts."""
    results = []
    for item in ctx["content"]:
        rec = recommend(item, ctx)
        results.append(rec)
    return results