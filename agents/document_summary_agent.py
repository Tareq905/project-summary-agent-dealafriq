from utils.llm_client import llm_summary
from rag.retriever import retrieve_context
from services.nsl_reasoner import apply_document_logic

def run_document_summary(doc):
    # 1. Get document logic (e.g., "Document has no key points")
    logical_facts = apply_document_logic(doc)
    
    # 2. Get RAG context for governance rules
    context = retrieve_context("contract terms delivery commitment dependency rules")

    # 3. Create a strict prompt with double curly braces {{ }} to avoid ValueErrors
    prompt = f"""
    Rules & Governance: {context}
    Mathematical Facts: {logical_facts}
    
    DOCUMENT METADATA:
    FileName: {doc.get('fileName')}
    Manual Key Points: {doc.get('keyPoints') if doc.get('keyPoints') else "None provided"}

    TASK:
    Analyze the document and return a JSON object. 
    If the document lacks content or key points, you MUST flag this as a RISK or ISSUE regarding "Documentation Integrity."

    REQUIRED JSON STRUCTURE:
    {{
      "summary": "High-level overview of the document's purpose",
      "action_points": ["List specific follow-ups or missing requirements"],
      "discussion_points": ["List core topics or gaps in information"],
      "notes": "Observations on document validity",
      "raidd_flags": {{
        "risks": [],
        "issues": [],
        "dependencies": [],
        "decisions": []
      }}
    }}

    STRICT MODULAR RULE FOR RAIDD ITEMS:
    Every entry in the raidd_flags lists MUST be an object:
    {{
      "category": "Risk | Issue | Decision | Dependency",
      "status": "High | Medium | Low",
      "ai_summary": "One paragraph explaining the impact of this document (or lack of info) on the project.",
      "details": ["Specific evidence from the filename or facts"]
    }}
    """
    
    return llm_summary(prompt)