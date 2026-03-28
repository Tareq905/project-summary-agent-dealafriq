def run_health_score(project, nsl_res):
    # 1. Try to get score from backend first
    score = 0
    health_records = project.get("health", [])
    if health_records and health_records[0].get("score"):
        score = health_records[0].get("score")
    else:
        # 2. Fallback: Calculate based on Milestone Completion (Math from NSL)
        # If project is COMPLETED, base is 100. Otherwise, use work completion pct.
        if project.get("status") == "COMPLETED":
            score = 100
        else:
            score = nsl_res.get("work_pct", 0)

    # 3. Penalties (Adjust score based on performance)
    # Penalty for Overdue Milestones (-10 per item)
    overdue_penalty = nsl_res.get("overdue_count", 0) * 10
    score -= overdue_penalty

    # Penalty for Velocity Gap (If time passed is much higher than work done)
    time_pct = nsl_res.get("time_pct", 0)
    work_pct = nsl_res.get("work_pct", 0)
    if time_pct > (work_pct + 20):  # More than 20% lag
        score -= 5

    # Penalty for Pending Action Points (-2 per item)
    for meeting in project.get("meetings", []):
        for ap in meeting.get("actionPoints", []):
            if ap.get("status") == "PENDING":
                score -= 2

    # Ensure score is within 0-100 range
    return max(min(score, 100), 0)