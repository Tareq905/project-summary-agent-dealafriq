from utils.llm_client import llm_summary
from services.nsl_reasoner import apply_nsl_logic
from rag.retriever import retrieve_context

def run_project_summary(project):
    logical_facts = apply_nsl_logic(project)
    context = retrieve_context("PMO reporting RAIDD governance monitoring STATUS_RULE")

    # This combines your specific prompt with the 'flag' requirement
    prompt = f"""
    Rules: {context}
    Logical Facts: {logical_facts}
    
    Project Data:
    Name: {project.get('name')}
    Tasks: {project.get('tasks')}
    Milestones: {project.get('milestones')}
    Health: {project.get('health')}

    Task: Analyze the overall project and return a JSON object.
    
    FLAG LOGIC:
    - Determine a 'flag' value: "Red" (blocking issues), "Amber" (risks/delays), or "Green" (on track).
    
    JSON KEYS REQUIRED:
    - 'summary': High-level overview of the project's current status.
    - 'action_points': List specific project-level next steps.
    - 'discussion_points': List the core focus areas or recent strategic shifts.
    - 'notes': Any general observations about team velocity or health.
    - 'flag': The determined Red/Amber/Green status.
    - 'raidd_flags': Identify Risks, Assumptions, Issues, Dependencies, and Decisions based on task delays or milestone status.
    """
    
    return llm_summary(prompt)