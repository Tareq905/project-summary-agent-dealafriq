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
    - Total Tasks: {len(project.get('tasks', []))}
    - Task Details: {project.get('tasks')}
    - Milestones: {project.get('milestones')}
    - Recent Meetings: {meeting_context}

    TASK:
    Analyze the project velocity and health. You must specifically evaluate Task completion (Total vs. Completed), Task Start/End dates, and RAIDD status.

    HEALTH LABEL LOGIC (REQUIRED):
    Assign exactly one string value to "health_label":
    - "Excellent": All Tasks and Milestones are completed or strictly on schedule. High task completion ratio relative to elapsed time. Zero overdue items.
    - "Good": Project is progressing. Most tasks meet their Start/End dates. No overdue Milestones. RAIDD items are minor and managed.
    - "Bad": Any Task or Milestone is past its "endDate" or "milestoneDate" but status is NOT "COMPLETED". Also "Bad" if there are critical RAIDD issues or a major lag in task completion.

    VERDICT & FLAG LOGIC:
    - "Red": If facts show "OVERDUE" tasks/milestones or health is "Bad".
    - "Amber": If tasks are near expiration or timeline is progressing faster than task completion.
    - "Green": If all items are on track and health is "Good" or "Excellent".

    REQUIRED JSON KEYS:
    - "health_label": (STRING: "Excellent", "Good", or "Bad". MUST NOT BE AN ARRAY.)
    - "summary": (Use 🔹 icons. Summarize task progress and deadline adherence.)
    - "weekly_summary": (Concise overview of the week's progress.)
    - "flag": ("Red", "Amber", or "Green")
    - "action_points": [Specific next steps]
    - "discussion_points": [Core focus areas]
    - "notes": "General observations."
    - "raidd_flags": {{
        "risks": [],
        "assumptions": [],
        "issues": [],
        "dependencies": [],
        "decisions": []
      }}

    STRICT RULES:
    1. 'health_label' MUST be a string, not a list.
    2. Every RAIDD entry MUST be a descriptive paragraph string.
    3. If Milestones and Tasks are empty, health is "Bad", flag is "Red", and add an 'Uninitialized' issue in raidd_flags.
    """
    
    return llm_summary(prompt)