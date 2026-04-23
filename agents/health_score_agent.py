def run_health_score(project, nsl_res):
    milestones = project.get("milestones", [])
    tasks = project.get("tasks", [])
    
    if not milestones and not tasks:
        return 0.0

    # Start with work completion or baseline
    score = nsl_res.get("work_pct", 0)
    if score == 0: score = 80 # Baseline if tasks exist but milestones are upcoming

    # Penalty for overdue milestones (-20 each)
    score -= (nsl_res.get("overdue_count", 0) * 20)

    # Penalty for overdue tasks (-5 each)
    score -= (nsl_res.get("overdue_tasks", 0) * 5)
    
    if project.get("status") == "COMPLETED": score = 100
    elif project.get("status") == "CANCELLED": score = 0
        
    return max(min(score, 100), 0)