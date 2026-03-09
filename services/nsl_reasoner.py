from datetime import datetime, timezone

def apply_nsl_logic(project):
    logical_facts = []
    
    # 1. Timeline Math
    start_str = project.get("startDate")
    end_str = project.get("endDate")
    now = datetime.now(timezone.utc)

    if start_str and end_str:
        s_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        e_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        total_days = (e_dt - s_dt).days
        elapsed = (now - s_dt).days
        
        if total_days > 0:
            time_pct = min(max((elapsed / total_days) * 100, 0), 100)
            logical_facts.append(f"Timeline: {time_pct:.1f}% of scheduled time has passed.")

    # 2. Work Math
    milestones = project.get("milestones", [])
    total_m = len(milestones)
    done_m = len([m for m in milestones if m.get("status") == "COMPLETED"])
    
    work_pct = (done_m / total_m * 100) if total_m > 0 else 0
    logical_facts.append(f"Completion: {work_pct:.1f}% of milestones are finished.")

    # 3. Specific Alerts for RAIDD Paragraphs
    for m in milestones:
        if m.get("status") != "COMPLETED" and m.get("milestoneDate"):
            m_dt = datetime.fromisoformat(m.get("milestoneDate").replace("Z", "+00:00"))
            if m_dt < now:
                logical_facts.append(f"CRITICAL: Milestone '{m.get('title')}' is overdue. This creates a bottleneck.")

    return {
        "facts": logical_facts,
        "progress_str": f"{work_pct:.1f}%"
    }

def apply_document_logic(doc):
    facts = []
    if not doc.get("keyPoints"): facts.append("Document has no extracted key points to validate.")
    return facts