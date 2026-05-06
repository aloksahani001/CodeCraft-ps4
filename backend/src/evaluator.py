"""
Evaluator — Issue 18
Mirrors the official scoring script exactly:
  engagement  = base_engagement × activity_score × avg_engagement  (50%)
  timing      = activity_score at chosen slot                       (20%)
  platform    = SHORT+IG=1.0, LONG+YT=1.0, SHORT+YT=0.85, LONG+IG=0.7 (15%)
  efficiency  = max(0, 1 - latency_seconds)                         (15%)
"""

PLATFORM_QUALITY = {
    ("SHORT", "Instagram"): 1.00,
    ("LONG",  "YouTube"):   1.00,
    ("SHORT", "YouTube"):   0.85,
    ("LONG",  "Instagram"): 0.70,
}

WEIGHTS = {
    "engagement": 0.50,
    "timing":     0.20,
    "platform":   0.15,
    "efficiency": 0.15,
}


def compute_metrics(recommendations, ctx, latency_seconds=0.0):
    if not recommendations:
        return {}

    content_map  = {item["content_id"]: item for item in ctx["content"]}
    hist         = ctx["historical_engagement"]
    activity     = ctx["platform_activity"]
    creators     = ctx["creators"]
    creator_avg  = ctx["creator_avg_engagement"]
    global_avg   = ctx["global_avg_engagement"]

    engagement_total     = 0.0
    timing_total         = 0.0
    platform_score_total = 0.0

    for rec in recommendations:
        cid          = rec["content_id"]
        platform     = rec["platform"]
        time_slot    = rec["time_slot"]

        item         = content_map[cid]
        creator_id   = item["creator_id"]
        content_type = item["content_type"]

        act  = activity.get((platform, time_slot), 0.6)
        key  = (creator_id, platform, content_type, time_slot)
        h    = hist.get(key, creator_avg.get(creator_id, global_avg))
        base = creators[creator_id]["base_engagement"] if creator_id in creators else 1.0

        engagement_total     += base * act * h
        timing_total         += act
        platform_score_total += PLATFORM_QUALITY.get((content_type, platform), 0.7)

    efficiency_score = max(0.0, 1.0 - latency_seconds)

    n = len(recommendations)
    raw_engagement   = engagement_total / n
    timing_score     = timing_total / n
    platform_score   = platform_score_total / n
    engagement_score = min(raw_engagement, 1.5) / 1.5

    final_score = (
        WEIGHTS["engagement"] * engagement_score +
        WEIGHTS["timing"]     * timing_score     +
        WEIGHTS["platform"]   * platform_score   +
        WEIGHTS["efficiency"] * efficiency_score
    )

    return {
        "engagement_score":  engagement_score,
        "timing_score":      timing_score,
        "platform_score":    platform_score,
        "efficiency_score":  efficiency_score,
        "final_score":       final_score,
        "raw_engagement":    raw_engagement,
        "n":                 n,
        "n_post_now":        sum(1 for r in recommendations if r["decision"] == "POST_NOW"),
        "n_schedule":        sum(1 for r in recommendations if r["decision"] == "SCHEDULE"),
        "n_instagram":       sum(1 for r in recommendations if r["platform"] == "Instagram"),
        "n_youtube":         sum(1 for r in recommendations if r["platform"] == "YouTube"),
    }


def print_metrics(metrics):
    print("\n--- SCORE BREAKDOWN ---")
    print(f"Engagement Score:  {metrics['engagement_score']:.4f}  (raw={metrics['raw_engagement']:.4f}, w=0.50)")
    print(f"Timing Score:      {metrics['timing_score']:.4f}  (w=0.20)")
    print(f"Platform Score:    {metrics['platform_score']:.4f}  (w=0.15)")
    print(f"Efficiency Score:  {metrics['efficiency_score']:.4f}  (w=0.15)")
    print("─────────────────────────────────")
    print(f"Final Score:       {metrics['final_score']:.4f}")
    print(f"\nBreakdown: {metrics['n']} recs | "
          f"POST_NOW={metrics['n_post_now']} SCHEDULE={metrics['n_schedule']} | "
          f"Instagram={metrics['n_instagram']} YouTube={metrics['n_youtube']}")