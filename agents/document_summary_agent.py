from utils.llm_client import llm_summary
from rag.retriever import retrieve_context
from services.nsl_reasoner import apply_document_logic

def run_document_summary(doc):
    # 1. Get document logic and contract/dependency rules
    logical_facts = apply_document_logic(doc)
    context = retrieve_context("contract terms delivery commitment dependency rules")

    prompt = f"""
    Rules: {context}
    Document Facts: {logical_facts}
    
    Document Metadata:
    FileName: {doc.get('fileName')}
    Manual Key Points: {doc.get('keyPoints')}

    Task: Analyze the document purpose and return a JSON object.
    - 'summary': What is this document and why was it uploaded?
    - 'action_points': List any requirements or follow-ups triggered by this document.
    - 'discussion_points': List the core topics covered in the document.
    - 'notes': Observations on document validity or missing information.
    - 'raidd_flags': Does this document create a Dependency (e.g. unsigned contract) or a Risk?
    """
    
    return llm_summary(prompt)