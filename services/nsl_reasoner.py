from datetime import datetime, timezone

def apply_nsl_logic(project):
    """
    Mathematical logic for Project Velocity.
    Upgraded to specifically analyze Task completion ratios and Date adherence.
    """
    facts = []
    start_str = project.get("startDate")
    end_str = project.get("endDate")
    now = datetime.now(timezone.utc)

    milestones = project.get("milestones", [])
    tasks = project.get("tasks", [])

    # 1. Uninitialized Project Check (The "Danob" Rule)
    if not milestones and not tasks:
        facts.append("RAIDD_ISSUE: Project is currently uninitialized. No Work Breakdown Structure (WBS), tasks, or milestones have been defined.")
        facts.append("RAIDD_RISK: Lack of project structure prevents any execution progress.")
        return {
            "facts": facts, "progress_str": "0.0%", "work_pct": 0, "time_pct": 0,
            "overdue_count": 0, "overdue_tasks": 0, "high_priority_overdue": 0,
            "task_completion_ratio": "0/0"
        }

    # 2. Project Timeline Progress Calculation
    time_pct = 0
    if start_str and end_str:
        try:
            s_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            e_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            total_days = (e_dt - s_dt).days
            elapsed = (now - s_dt).days
            if total_days > 0:
                time_pct = min(max((elapsed / total_days) * 100, 0), 100)
                facts.append(f"FACT: Project is {time_pct:.1f}% through its total scheduled duration.")
        except: pass

    # 3. Task-Level Completion and Date Adherence (Upgraded Logic)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "COMPLETED"])
    overdue_tasks = 0
    high_priority_overdue = 0
    
    facts.append(f"FACT: Task Completion Ratio is {completed_tasks} out of {total_tasks} total tasks.")

    for t in tasks:
        t_status = t.get("status")
        t_priority = (t.get("priority") or "MEDIUM").upper()
        t_start = t.get("startDate")
        t_end = t.get("endDate")
        
        if t_status != "COMPLETED":
            # Check if Task should have started but hasn't
            if t_start and t_status == "UPCOMING":
                try:
                    t_start_dt = datetime.fromisoformat(t_start.replace("Z", "+00:00"))
                    if t_start_dt < now:
                        facts.append(f"RAIDD_ISSUE: Task '{t.get('title')}' failed to start on schedule (Planned Start: {t_start_dt.date()}).")
                except: pass

            # Check if Task is past its End Date
            if t_end:
                try:
                    t_end_dt = datetime.fromisoformat(t_end.replace("Z", "+00:00"))
                    if t_end_dt < now:
                        overdue_tasks += 1
                        facts.append(f"RAIDD_ISSUE: Task '{t.get('title')}' is OVERDUE (Planned End: {t_end_dt.date()}).")
                        if t_priority == "HIGH":
                            high_priority_overdue += 1
                except: pass

    # 4. Milestone Math and RAIDD Status
    total_m = len(milestones)
    done_m = len([m for m in milestones if m.get("status") == "COMPLETED"])
    work_pct = (done_m / total_m * 100) if total_m > 0 else 0
    facts.append(f"FACT: Milestone completion progress is {work_pct:.1f}%.")

    overdue_milestones = 0
    for m in milestones:
        if m.get("status") != "COMPLETED" and m.get("milestoneDate"):
            try:
                m_dt = datetime.fromisoformat(m.get("milestoneDate").replace("Z", "+00:00"))
                if m_dt < now:
                    overdue_milestones += 1
                    facts.append(f"RAIDD_ISSUE: Milestone '{m.get('title')}' is critically OVERDUE (Target: {m_dt.date()}).")
            except: continue

    # 5. Velocity Check
    if time_pct > (work_pct + 15) and project.get("status") == "ONGOING":
        facts.append(f"RAIDD_RISK: Significant velocity gap detected. Timeline elapsed ({time_pct:.1f}%) exceeds work progress ({work_pct:.1f}%).")

    return {
        "facts": facts,
        "progress_str": f"{work_pct:.1f}%",
        "work_pct": work_pct,
        "time_pct": time_pct,
        "overdue_count": overdue_milestones,
        "overdue_tasks": overdue_tasks,
        "high_priority_overdue": high_priority_overdue,
        "task_completion_ratio": f"{completed_tasks}/{total_tasks}"
    }

def apply_document_logic(doc):
    """
    Logic for Document Integrity (Maintained for consistency).
    """
    facts = []
    filename = (doc.get("fileName") or "").lower()
    key_points = doc.get("keyPoints") or []

    if not key_points:
        facts.append("RAIDD_ISSUE: Document has no extracted key points. Integrity cannot be verified.")

    if any(k in filename for k in ["contract", "agreement", "sow", "signed"]):
        facts.append("RAIDD_DEPENDENCY: Formal agreement detected. Execution depends on valid signatures.")
    
    return facts