from datetime import datetime, timezone


def apply_nsl_logic(project):
    """
    Mathematical logic for Project Velocity.
    Generates deterministic RAIDD facts across all 5 categories:
    RISK, ISSUE, ASSUMPTION, DEPENDENCY, DECISION.
    Used by: project_summary_agent, health_score_agent, intelligence_orchestrator.
    """
    facts = []
    start_str = project.get("startDate")
    end_str   = project.get("endDate")
    now       = datetime.now(timezone.utc)

    milestones = project.get("milestones", [])
    tasks      = project.get("tasks", [])
    meetings   = project.get("meetings", [])
    status     = project.get("status", "")

    # ── 1. Uninitialized Project Check ───────────────────
    if not milestones and not tasks:
        facts.append("RAIDD_ISSUE: Project is currently uninitialized. No Work Breakdown Structure (WBS), tasks, or milestones have been defined.")
        facts.append("RAIDD_RISK: Lack of project structure prevents any execution progress or delivery visibility.")
        facts.append("RAIDD_ASSUMPTION: It is assumed that work is happening informally without any tracked structure or accountability.")
        facts.append("RAIDD_DEPENDENCY: All future project phases depend on a WBS and task structure being defined first before any execution can begin.")
        facts.append("RAIDD_DECISION: An immediate decision is required to initialize the project structure, assign tasks, and define milestones before further time is lost.")
        return {
            "facts": facts, "progress_str": "0.0%", "work_pct": 0, "time_pct": 0,
            "overdue_count": 0, "overdue_tasks": 0, "high_priority_overdue": 0,
            "task_completion_ratio": "0/0"
        }

    # ── 2. Project Timeline Progress ─────────────────────
    time_pct  = 0
    days_left = None
    if start_str and end_str:
        try:
            s_dt       = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            e_dt       = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            total_days = (e_dt - s_dt).days
            elapsed    = (now - s_dt).days
            days_left  = (e_dt - now).days

            if total_days > 0:
                time_pct = min(max((elapsed / total_days) * 100, 0), 100)
                facts.append(f"FACT: Project is {time_pct:.1f}% through its total scheduled duration.")

            # Deadline proximity risk
            if days_left is not None:
                if days_left < 0:
                    facts.append(f"RAIDD_ISSUE: Project end date has passed ({e_dt.date()}). The project is running beyond its scheduled deadline.")
                elif days_left <= 7:
                    facts.append(f"RAIDD_RISK: Project deadline is critically near — only {days_left} day(s) remaining (End: {e_dt.date()}).")
                elif days_left <= 14:
                    facts.append(f"RAIDD_RISK: Project deadline is approaching — {days_left} days remaining (End: {e_dt.date()}). Completion must be validated.")

        except:
            pass
    else:
        facts.append("RAIDD_ASSUMPTION: No start or end date has been defined. It is assumed the project timeline is open-ended, which prevents any deadline tracking.")

    # ── 3. Task-Level Analysis ───────────────────────────
    total_tasks     = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "COMPLETED"])
    ongoing_tasks   = [t for t in tasks if t.get("status") == "ONGOING"]
    upcoming_tasks  = [t for t in tasks if t.get("status") == "UPCOMING"]
    overdue_tasks        = 0
    high_priority_overdue = 0

    facts.append(f"FACT: Task Completion Ratio is {completed_tasks} out of {total_tasks} total tasks.")

    # Assumption: upcoming tasks assume prior ones will finish on time
    if upcoming_tasks and ongoing_tasks:
        facts.append(
            f"RAIDD_ASSUMPTION: {len(upcoming_tasks)} upcoming task(s) assume that {len(ongoing_tasks)} currently ongoing task(s) "
            f"will complete on schedule. No formal dependency confirmation is in place."
        )

    # Assumption: no tasks completed yet on an active project
    if completed_tasks == 0 and total_tasks > 0 and status == "ONGOING":
        facts.append("RAIDD_ASSUMPTION: It is assumed the project has not formally started execution, as zero tasks have been marked completed despite the project being active.")

    for t in tasks:
        t_status   = t.get("status")
        t_priority = (t.get("priority") or "MEDIUM").upper()
        t_title    = t.get("title", "Unnamed Task")
        t_start    = t.get("startDate")
        t_end      = t.get("endDate")

        if t_status != "COMPLETED":

            # Task failed to start on time
            if t_start and t_status == "UPCOMING":
                try:
                    t_start_dt = datetime.fromisoformat(t_start.replace("Z", "+00:00"))
                    if t_start_dt < now:
                        facts.append(f"RAIDD_ISSUE: Task '{t_title}' failed to start on schedule (Planned Start: {t_start_dt.date()}).")
                        facts.append(f"RAIDD_DECISION: A decision is needed on whether to reassign or reschedule Task '{t_title}', which has not started despite its planned start date passing.")
                except:
                    pass

            # Task is overdue
            if t_end:
                try:
                    t_end_dt = datetime.fromisoformat(t_end.replace("Z", "+00:00"))
                    if t_end_dt < now:
                        overdue_tasks += 1
                        facts.append(f"RAIDD_ISSUE: Task '{t_title}' is OVERDUE (Planned End: {t_end_dt.date()}).")

                        if t_priority == "HIGH":
                            high_priority_overdue += 1
                            facts.append(f"RAIDD_RISK: High-priority task '{t_title}' is overdue. This poses a direct risk to project delivery and milestone achievement.")
                            facts.append(f"RAIDD_DECISION: An urgent decision is required to escalate, reassign, or descope high-priority task '{t_title}' to prevent further timeline slippage.")
                        else:
                            facts.append(f"RAIDD_DECISION: A decision is needed on whether to extend, reassign, or deprioritize task '{t_title}' which is currently overdue.")

                        # Dependency: next tasks may be blocked
                        facts.append(f"RAIDD_DEPENDENCY: Downstream tasks or milestones that depend on '{t_title}' are at risk of being blocked until this overdue task is resolved.")
                except:
                    pass

    # ── 4. Milestone Analysis ────────────────────────────
    total_m = len(milestones)
    done_m  = len([m for m in milestones if m.get("status") == "COMPLETED"])
    work_pct = (done_m / total_m * 100) if total_m > 0 else 0
    facts.append(f"FACT: Milestone completion progress is {work_pct:.1f}% ({done_m}/{total_m} completed).")

    overdue_milestones = 0
    for m in milestones:
        m_title = m.get("title", "Unnamed Milestone")
        if m.get("status") != "COMPLETED" and m.get("milestoneDate"):
            try:
                m_dt = datetime.fromisoformat(m.get("milestoneDate").replace("Z", "+00:00"))
                if m_dt < now:
                    overdue_milestones += 1
                    facts.append(f"RAIDD_ISSUE: Milestone '{m_title}' is critically OVERDUE (Target: {m_dt.date()}).")
                    facts.append(f"RAIDD_RISK: Overdue milestone '{m_title}' directly threatens the project delivery schedule and stakeholder commitments.")
                    facts.append(f"RAIDD_DECISION: A decision is required on whether to escalate milestone '{m_title}' to stakeholders or revise the project delivery plan.")
            except:
                continue

    # Assumption: milestones with no tasks assume work is tracked informally
    milestones_without_tasks = [m for m in milestones if not m.get("tasks")]
    if milestones_without_tasks:
        facts.append(
            f"RAIDD_ASSUMPTION: {len(milestones_without_tasks)} milestone(s) have no linked tasks. "
            f"It is assumed that related work is being tracked informally outside the system."
        )

    # Dependency: incomplete milestones block next phase
    incomplete_milestones = [m for m in milestones if m.get("status") != "COMPLETED"]
    if incomplete_milestones:
        facts.append(
            f"RAIDD_DEPENDENCY: {len(incomplete_milestones)} incomplete milestone(s) are blocking progression "
            f"to the next project phase. Completion is required before phase transition."
        )

    # ── 5. Velocity Check ────────────────────────────────
    if time_pct > (work_pct + 15) and status == "ONGOING":
        facts.append(
            f"RAIDD_RISK: Significant velocity gap detected. Timeline elapsed ({time_pct:.1f}%) "
            f"exceeds milestone progress ({work_pct:.1f}%). Current pace will not meet the deadline."
        )
        facts.append(
            f"RAIDD_DECISION: A decision is needed on whether to accelerate delivery, reduce scope, "
            f"or revise the project end date given the current velocity gap of {time_pct - work_pct:.1f}%."
        )
        facts.append(
            f"RAIDD_ASSUMPTION: It is assumed the remaining {100 - work_pct:.1f}% of work can be completed "
            f"within the remaining {100 - time_pct:.1f}% of the scheduled timeline, which is currently unvalidated."
        )

    # ── 6. Meeting Coverage Check ────────────────────────
    if not meetings and status == "ONGOING":
        facts.append("RAIDD_RISK: No meetings have been recorded for this project. Lack of communication tracking is a governance and alignment risk.")
        facts.append("RAIDD_ASSUMPTION: It is assumed stakeholder communication is happening informally without any recorded meeting or follow-up structure.")

    # ── 7. Task completion assumption vs timeline ────────
    if total_tasks > 0 and time_pct >= 50 and completed_tasks == 0:
        facts.append(
            f"RAIDD_RISK: Project is {time_pct:.1f}% through its timeline but has 0 completed tasks. "
            f"This is a critical delivery risk."
        )
        facts.append(
            "RAIDD_ASSUMPTION: It is assumed work is progressing but has not been formally marked complete in the system, "
            "which may indicate a tracking or accountability gap."
        )

    return {
        "facts":                  facts,
        "progress_str":           f"{work_pct:.1f}%",
        "work_pct":               work_pct,
        "time_pct":               time_pct,
        "overdue_count":          overdue_milestones,
        "overdue_tasks":          overdue_tasks,
        "high_priority_overdue":  high_priority_overdue,
        "task_completion_ratio":  f"{completed_tasks}/{total_tasks}"
    }


def apply_document_logic(doc):
    """
    Logic for Document Integrity.
    Used by: document_summary_agent.
    Return signature unchanged — list of fact strings.
    """
    facts    = []
    filename  = (doc.get("fileName") or "").lower()
    key_points = doc.get("keyPoints") or []

    if not key_points:
        facts.append("RAIDD_ISSUE: Document has no extracted key points. Content integrity cannot be verified.")
        facts.append("RAIDD_ASSUMPTION: It is assumed the document contains valid and complete information, though no key points have been extracted to confirm this.")

    if any(k in filename for k in ["contract", "agreement", "sow", "signed"]):
        facts.append("RAIDD_DEPENDENCY: A formal agreement document has been detected. Project execution depends on valid signatures and approval of this document.")
        facts.append("RAIDD_RISK: If this agreement is unsigned or outdated, it poses a contractual and delivery risk to the project.")

    if any(k in filename for k in ["invoice", "payment", "billing"]):
        facts.append("RAIDD_DEPENDENCY: A financial document has been detected. Payment or billing approvals may be required before project phases can proceed.")

    if any(k in filename for k in ["plan", "roadmap", "timeline", "schedule"]):
        facts.append("RAIDD_ASSUMPTION: It is assumed the plan or roadmap document reflects the current agreed project scope and has been reviewed by all stakeholders.")

    return facts