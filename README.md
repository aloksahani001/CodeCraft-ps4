# Creator Content Posting Optimization System

## Team Information
- **Team Name**: CodeCraft
- **Year**: 2nd Year
- **All-Female Team**: No

## Architecture Overview

Our system uses a deterministic scoring-based recommendation engine to identify the optimal posting platform and time slot for each content item. For every submission, the engine evaluates all possible combinations of platform and hourly posting slots, then selects the option with the highest predicted engagement score. This score is calculated using platform activity trends, creator-specific engagement history, and the creator’s base engagement profile to ensure recommendations are both personalized and data-driven.

Platform selection between Instagram and YouTube is handled through comparative scoring. The system naturally favors Instagram for SHORT content and YouTube for LONG content while still considering creator-specific historical performance to avoid rigid platform bias. This creates a balanced recommendation strategy that adapts to different creator behaviors and engagement patterns.

To balance global activity trends with creator-specific history, the scoring engine combines platform-wide activity scores with historical engagement metrics for the specific creator, platform, content type, and posting time. Missing or sparse historical data is handled using fallback averages to maintain robustness and consistency.

The scheduling decision is made by comparing the current posting slot with the predicted optimal slot. If the current slot achieves a near-optimal score, the system recommends POST_NOW; otherwise, it recommends SCHEDULE for improved engagement potential.