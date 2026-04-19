from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_project_summary(project, nsl_facts):
    # ... keep context retrieval logic ...
    prompt = f"""
    # ... keep factual data ...

    Task: Analyze the overall project and return a JSON object.
    
    IMPORTANT REQUIREMENT FOR RAIDD FLAGS:
    - Every item in 'risks', 'assumptions', 'issues', 'dependencies', and 'decisions' MUST be a simple string.
    - Each string must be a descriptive paragraph explaining the 'WHY' behind the flag and its impact.
    - DO NOT return objects or dictionaries inside these lists.

    JSON KEYS REQUIRED:
    - 'summary': High-level overview.
    - 'flag': Red/Amber/Green.
    - 'raidd_flags': {{ 
        "risks": ["descriptive paragraph string"], 
        "assumptions": [], 
        "issues": [], 
        "dependencies": [], 
        "decisions": [] 
      }}
    - 'action_points': [List of strings]
    - 'discussion_points': [List of strings]
    - 'notes': string
    """
    return llm_summary(prompt)