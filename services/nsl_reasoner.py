from datetime import datetime, timezone

def apply_nsl_logic(project):
    logical_facts = []
    
    start_str = project.get("startDate")
    end_str = project.get("endDate")
    now = datetime.now(timezone.utc)

    # 1. Timeline Math
    time_pct = 0
    if start_str and end_str:
        s_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        e_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        total_days = (e_dt - s_dt).days
        elapsed = (now - s_dt).days
        if total_days > 0:
            time_pct = min(max((elapsed / total_days) * 100, 0), 100)
            logical_facts.append(f"Timeline Math: {time_pct:.1f}% of duration has passed.")

    # 2. Work Math
    milestones = project.get("milestones", [])
    total_m = len(milestones)
    done_m = len([m for m in milestones if m.get("status") == "COMPLETED"])
    work_pct = (done_m / total_m * 100) if total_m > 0 else 0
    logical_facts.append(f"Work Math: {work_pct:.1f}% of milestones are finished.")

    # 3. Overdue Check
    overdue_count = 0
    for m in milestones:
        if m.get("status") != "COMPLETED" and m.get("milestoneDate"):
            m_dt = datetime.fromisoformat(m.get("milestoneDate").replace("Z", "+00:00"))
            if m_dt < now:
                overdue_count += 1
                logical_facts.append(f"CRITICAL: Milestone '{m.get('title')}' is OVERDUE.")

    return {
        "facts": logical_facts,
        "work_pct": work_pct,  # Numeric value for the score agent
        "time_pct": time_pct,  # Numeric value for the score agent
        "overdue_count": overdue_count,
        "progress_str": f"{work_pct:.1f}%"
    }

def apply_document_logic(doc):
    facts = []
    if not doc.get("keyPoints"): facts.append("Document has no key points.")
    return facts