from utils.llm_client import llm_summary
from rag.retriever import retrieve_context
from services.nsl_reasoner import apply_document_logic

def run_document_summary(doc):
    # 1. Get the broadened facts from NSL
    logical_facts = apply_document_logic(doc)
    
    # 2. Get RAG context
    context = retrieve_context("contract terms delivery commitment dependency rules RAIDD indicators")

    prompt = f"""
    Rules & Governance: {context}
    Deterministic Facts: {logical_facts}
    
    DOCUMENT METADATA:
    FileName: {doc.get('fileName')}
    Manual Key Points: {doc.get('keyPoints') if doc.get('keyPoints') else "No points extracted yet."}

    TASK:
    Analyze the document and provide a comprehensive intelligence report. 
    
    RAIDD IDENTIFICATION RULES:
    - RISKS: If this is a 'Best Practice' or 'Workflow' document, what is the risk of NOT following it?
    - ASSUMPTIONS: What must we assume is true for this document to be valid?
    - ISSUES: Are there missing key points or pending signatures mentioned?
    - DEPENDENCIES: What project phases are waiting for the information in this file?

    FORMATTING:
    - Return a JSON object with: summary, action_points, discussion_points, notes, raidd_flags.
    - summary: Must include a 🔹 icon.
    - raidd_flags: MUST contain lists of string paragraphs. 
    - DO NOT return empty categories if you can infer a logical flag from the FileName and Facts.

    STRICT RULE: Every RAIDD list item must be a 2-3 sentence string. No objects.
    """
    
    return llm_summary(prompt)