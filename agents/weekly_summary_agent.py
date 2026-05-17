from utils.llm_client import llm_summary

def run_weekly_summary(project, logs):
    tasks      = project.get("tasks", [])
    milestones = project.get("milestones", [])
    meetings   = project.get("meetings", [])

    # Task breakdown
    total_tasks     = len(tasks)
    completed_tasks = len([t for t in tasks if t.get("status") == "COMPLETED"])
    overdue_tasks   = [t for t in tasks if t.get("status") not in ("COMPLETED",) and t.get("endDate")]
    ongoing_tasks   = [t for t in tasks if t.get("status") == "ONGOING"]

    # Milestone breakdown
    total_milestones     = len(milestones)
    completed_milestones = len([m for m in milestones if m.get("status") == "COMPLETED"])
    overdue_milestones   = [m for m in milestones if m.get("status") != "COMPLETED" and m.get("milestoneDate")]

    # Recent meeting action points
    recent_actions = []
    for mtg in meetings:
        for ap in mtg.get("actionPoints", []):
            content = ap.get("content")
            if content:
                recent_actions.append(content)

    prompt = f"""
    You are a Project Management AI. Generate a concise weekly project status summary.

    PROJECT DATA:
    - Project Name: {project.get('name')}
    - Status: {project.get('status')}
    - Start Date: {project.get('startDate')}
    - End Date: {project.get('endDate')}

    TASK PROGRESS:
    - Total Tasks: {total_tasks}
    - Completed Tasks: {completed_tasks}
    - Ongoing Tasks: {[t.get('title') for t in ongoing_tasks]}
    - Overdue Tasks: {[t.get('title') for t in overdue_tasks]}

    MILESTONE PROGRESS:
    - Total Milestones: {total_milestones}
    - Completed Milestones: {completed_milestones}
    - Overdue Milestones: {[m.get('title') for m in overdue_milestones]}

    RECENT ACTION POINTS FROM MEETINGS:
    {recent_actions if recent_actions else "No recent action points."}

    TASK:
    Write a professional weekly summary covering:
    1. Overall project health this week
    2. Task completion progress
    3. Any overdue tasks or milestones (if any)
    4. Key risks or issues detected
    5. What needs attention next week

    RULES:
    - Be concise but informative (3-5 sentences)
    - Do NOT mention meeting names or transcripts
    - Focus purely on project progress and health
    - Return ONLY a JSON object with a single key: "weekly_summary"

    Example output:
    {{
        "weekly_summary": "This week, the project shows moderate progress with 3 out of 8 tasks completed. Two tasks are currently overdue which may impact the upcoming milestone deadline. The team should prioritize resolving the delayed API integration task. No critical risks have been identified beyond the timeline slippage."
    }}
    """

    result = llm_summary(prompt)

    # Extract only weekly_summary key
    if isinstance(result, dict):
        weekly_text = result.get("weekly_summary") or result.get("summary", "")
        return {"weekly_summary": weekly_text}

    return {"weekly_summary": str(result)}