from utils.llm_client import llm_summary
from services.nsl_reasoner import apply_nsl_logic
from rag.retriever import retrieve_context

def run_project_summary(project, nsl_facts):
    """
    Analyzes project status using RAG rules and Mathematical NSL facts.
    Returns a structured JSON with descriptive paragraph-style RAIDD flags.
    """
    # 1. Retrieve Governance and Status Rules from RAG
    context = retrieve_context("PMO reporting RAIDD governance monitoring STATUS_RULE")

    # 2. Construct the enriched prompt
    prompt = f"""
    Rules from Knowledge Base: {context}
    Mathematical Facts from NSL: {nsl_facts}
    
    Raw Project Data:
    - Name: {project.get('name')}
    - Tasks: {project.get('tasks')}
    - Milestones: {project.get('milestones')}
    - Health Data: {project.get('health')}

    Task: Analyze the overall project and return a JSON object.
    
    VERDICT & FLAG LOGIC:
    - Compare 'Timeline Progress' (time elapsed) against 'Completion Progress' (milestones done).
    - Determine 'flag': 
        * "Red" if milestones are OVERDUE or there is a massive velocity gap.
        * "Amber" if completion is lagging behind the timeline or risks are unresolved.
        * "Green" if work completed is equal to or ahead of the time elapsed.

    IMPORTANT REQUIREMENT FOR RAIDD FLAGS:
    - For every item in 'risks', 'assumptions', 'issues', 'dependencies', or 'decisions', do NOT write a single line.
    - Write a short paragraph explaining the "WHY" behind the flag and its specific impact on the project's success.

    JSON KEYS REQUIRED:
    - 'summary': High-level overview of the project's current status.
    - 'action_points': List of specific project-level next steps.
    - 'discussion_points': List of core focus areas or recent strategic shifts.
    - 'notes': Any general observations about team velocity or health.
    - 'flag': The determined Red/Amber/Green status.
    - 'raidd_flags': Object containing lists of DESCRIPTIVE PARAGRAPHS for: risks, assumptions, issues, dependencies, and decisions.
    """
    
    return llm_summary(prompt)