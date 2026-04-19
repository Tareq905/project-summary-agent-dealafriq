from utils.llm_client import llm_summary
from rag.retriever import retrieve_context
from services.nsl_reasoner import apply_document_logic

def run_document_summary(doc):
    # ... keep logic/context retrieval ...
    prompt = f"""
    # ... keep metadata ...

    Task: Analyze the document purpose and return a JSON object.
    
    RAIDD INSTRUCTION:
    - Return 'raidd_flags' as an object containing lists of strings.
    - Every list item must be a descriptive paragraph.
    - If a document is a contract awaiting signature, list it as a 'dependency' string.

    JSON KEYS REQUIRED:
    - 'summary': string
    - 'action_points': []
    - 'discussion_points': []
    - 'notes': string
    - 'raidd_flags': {{ "risks": [], "assumptions": [], "issues": [], "dependencies": [], "decisions": [] }}
    """
    return llm_summary(prompt)