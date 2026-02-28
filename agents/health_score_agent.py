def run_health_score(project):

    score = 0

    for health in project.get("health", []):
        if health.get("score"):
            score = health.get("score")

    for meeting in project.get("meetings", []):
        for ap in meeting.get("actionPoints", []):
            if ap.get("status") == "PENDING":
                score -= 5

    return max(score, 0)