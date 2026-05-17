from utils.llm_client import llm_summary
from rag.retriever import retrieve_context


def run_project_summary(project, nsl_facts, meeting_context):
    """
    Analyzes project status using RAG rules and Mathematical NSL facts.
    Upgraded to evaluate Health based on Task timelines and RAIDD status.
    """
    # 1. Retrieve the latest Governance and Status Rules from RAG
    context = retrieve_context("PMO reporting RAIDD governance monitoring STATUS_RULE")

    # 2. Construct the upgraded prompt
    prompt = f"""
    GOVERNANCE RULES:
    {context}

    MATHEMATICAL FACTS (DETERMINISTIC):
    {nsl_facts}

    RAW PROJECT DATA:
    - Name: {project.get('name')}
    - Status: {project.get('status')}
    - Start Date: {project.get('startDate')}
    - End Date: {project.get('endDate')}
    - Total Tasks: {len(project.get('tasks', []))}
    - Task Details: {project.get('tasks')}
    - Milestones: {project.get('milestones')}
    - Recent Meetings: {meeting_context}

    TASK:
    Analyze the project velocity and health. You must specifically evaluate Task completion
    (Total vs. Completed), Task Start/End dates, and ALL RAIDD categories.

    HEALTH LABEL LOGIC (REQUIRED):
    Assign exactly one string value to "health_label":
    - "Excellent": All Tasks and Milestones are completed or strictly on schedule.
      High task completion ratio relative to elapsed time. Zero overdue items.
    - "Good": Project is progressing. Most tasks meet their Start/End dates.
      No overdue Milestones. RAIDD items are minor and managed.
    - "Bad": Any Task or Milestone is past its "endDate" or "milestoneDate" but status
      is NOT "COMPLETED". Also "Bad" if there are critical RAIDD issues or a major lag
      in task completion.

    VERDICT & FLAG LOGIC:
    - "Red": If facts show "OVERDUE" tasks/milestones or health is "Bad".
    - "Amber": If tasks are near expiration or timeline is progressing faster than task completion.
    - "Green": If all items are on track and health is "Good" or "Excellent".

    REQUIRED JSON KEYS:
    - "health_label": (STRING: "Excellent", "Good", or "Bad". MUST NOT BE AN ARRAY.)
    - "summary": (Use 🔹 icons. Summarize task progress and deadline adherence.)
    - "weekly_summary": (Concise overview of the week's progress.)
    - "flag": ("Red", "Amber", or "Green")
    - "action_points": [Specific next steps based on task and milestone status]
    - "discussion_points": [Core focus areas for next team meeting]
    - "notes": "General observations about project health and team performance."
    - "raidd_flags": {{
        "risks": [],
        "assumptions": [],
        "issues": [],
        "dependencies": [],
        "decisions": []
      }}

    ══════════════════════════════════════════════════════
    RAIDD DETECTION RULES — MANDATORY. ALL 5 CATEGORIES.
    ══════════════════════════════════════════════════════

    You MUST analyze the project data and populate ALL 5 RAIDD categories.
    Do NOT leave any category empty if evidence exists. Each item must be a
    descriptive paragraph of 2-3 sentences.

    RISKS — What could go wrong or is likely to cause future failure?
    Look for:
    - Tasks or milestones approaching their deadline but not yet completed
    - High priority tasks that are ONGOING or UPCOMING with tight timelines
    - Velocity gap: timeline elapsed % significantly higher than work completion %
    - Low task completion ratio relative to project timeline consumed
    - Project end date is near but many tasks remain incomplete
    - No meetings recorded (communication risk)
    - Pattern of repeated overdue items
    Example: "The project has consumed 65% of its timeline but only 30% of tasks
    are completed, posing a significant delivery risk if the current velocity is
    not improved immediately."

    ASSUMPTIONS — What is being taken for granted without formal confirmation?
    Look for:
    - Tasks marked UPCOMING that assume prior tasks will finish on time
    - Project start/end dates that assume resource availability
    - No SLA or contract terms visible — assuming informal agreement is sufficient
    - Assuming external dependencies will be delivered on time
    - Assuming team capacity remains unchanged throughout the project
    - Milestones with no linked tasks — assuming work is happening informally
    Example: "It is assumed that all upstream task dependencies will be resolved
    on schedule, though no formal confirmation or tracking mechanism is in place
    to validate this assumption."

    ISSUES — What problems currently exist and are actively blocking progress?
    Look for:
    - Tasks or milestones with status NOT "COMPLETED" but past their end date (OVERDUE)
    - Tasks stuck in ONGOING status for extended periods
    - Tasks that failed to start (UPCOMING but past their startDate)
    - Zero task completion on an active project
    - Missing milestones or tasks entirely (uninitialized project)
    - No meeting records on a long-running project
    Example: "Three tasks are currently overdue with no completion recorded,
    directly blocking milestone progress and putting the project delivery date
    at immediate risk."

    DEPENDENCIES — What must happen before progress can continue?
    Look for:
    - Tasks that are UPCOMING and depend on ONGOING tasks completing first
    - Milestones that require all preceding tasks to be COMPLETED
    - External teams, APIs, or third-party deliverables referenced in task names
    - Meeting action points that are waiting on client or stakeholder approval
    - Document signatures or approvals blocking next phase
    - Any task whose startDate is after another task's endDate
    Example: "The UAT phase cannot begin until the backend integration task is
    marked complete, creating a hard sequential dependency that currently has
    no confirmed resolution date."

    DECISIONS — What decisions are pending, overdue, or need to be made?
    Look for:
    - No project health or scope decisions made despite overdue items
    - Tasks that have been ONGOING too long — a prioritization decision is needed
    - Whether to escalate overdue milestones to stakeholders
    - Resource allocation decisions needed due to task overload
    - Whether to revise the project end date given current velocity
    - Go/no-go decisions for upcoming phases with unresolved blockers
    - Meeting action points that require a decision but remain unresolved
    Example: "A decision is urgently needed on whether to extend the project
    deadline or reduce scope, given that 4 tasks are overdue and the current
    completion rate cannot meet the original delivery date."

    ══════════════════════════════════════════════════════
    RAIDD STRICT RULES:
    ══════════════════════════════════════════════════════
    1. ALL 5 categories MUST have at least 1 item if ANY project data exists.
    2. Each item MUST be a 2-3 sentence descriptive paragraph string.
    3. Base every item on ACTUAL data from Task Details, Milestones, Dates, and Facts.
    4. Do NOT return generic statements. Reference actual task names, dates, or counts.
    5. Do NOT leave risks, assumptions, dependencies, or decisions empty.
    6. If Milestones and Tasks are both empty: health is "Bad", flag is "Red",
       and populate issues with an "Uninitialized project" entry, risks with
       "No structure means no delivery visibility", assumptions with "Work is
       assumed to be happening informally", dependencies with "All future phases
       depend on WBS being defined first", decisions with "Decision needed to
       initialize project structure immediately."

    STRICT OUTPUT RULES:
    1. 'health_label' MUST be a single string, never a list.
    2. Every RAIDD entry MUST be a descriptive paragraph string, never an object.
    3. Return only a valid JSON object. No markdown, no extra text.
    """

    return llm_summary(prompt)