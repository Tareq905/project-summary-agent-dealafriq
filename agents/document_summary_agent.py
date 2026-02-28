from utils.llm_client import llm_summary  # REMOVED 'app.'
from rag.retriever import retrieve_context
from services.nsl_reasoner import apply_document_logic

def run_document_summary(document):
    governance_context = retrieve_context("contract approval dependency execution")
    logical_facts = apply_document_logic(document)

    prompt = f"""
    Document Data: {document}
    Governance Context: {governance_context}
    Logical Facts: {logical_facts}

    Provide document summary.
    """
    return llm_summary(prompt)