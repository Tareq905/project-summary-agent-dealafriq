from utils.llm_client import llm_summary
from services.nsl_reasoner import apply_nsl_logic
from rag.retriever import retrieve_context

def run_project_summary(project):

    logic = apply_nsl_logic(project)
    ctx = retrieve_context("project governance rules")

    prompt = f"""
    Project Data: {project}
    Governance Rules: {ctx}
    Logical Facts: {logic}

    Provide overall project summary.
    """

    return llm_summary(prompt)