import json
from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_transcript_deep_analysis(meeting_data):
    rules_context = retrieve_context("MEETING_RAIDD_EXTRACTION EMAIL_RAIDD_DEFINITIONS RAIDD_STRUCTURE")

    kps = "\n".join([f"- {kp.get('content')}" for kp in meeting_data.get("keyPoints", [])])
    aps = "\n".join([f"- {ap.get('content')}" for ap in meeting_data.get("actionPoints", [])])
    notes = meeting_data.get("notes", "")
    proj_desc = meeting_data.get("project", {}).get("description", "")
    
    content_to_analyze = f"""
    PROJECT DESCRIPTION: {proj_desc}
    MEETING NOTES: {notes}
    KEY POINTS DISCUSSED: {kps}
    ACTION ITEMS ASSIGNED: {aps}
    """

    system_instruction = """
    You are a Senior Project Management Intelligence Auditor. 
    Your goal is to perform a deep-dive RAIDD analysis. 
    DO NOT provide a generic 'Informational' summary. 
    You must evaluate the IMPACT of every meeting point on the project's success.
    
    CRITICAL ANALYSIS RULES:
    1. CATEGORY: Every meeting with Action Points should likely be categorized as 'Dependency' or 'Risk'.
    2. RAIDD ANALYSIS: Each field must be a list of descriptive paragraphs (2-3 sentences each). 
    3. INFERENCE: If a plan is missing or testing is needed, infer the RISK of failure or the ISSUE of technical debt.
    """

    user_prompt = f"""
    RAG GOVERNANCE RULES:
    {rules_context}
    
    DATA FOR EVALUATION:
    {content_to_analyze}

    OUTPUT FORMAT:
    You must return a strictly valid JSON matching this exact structure:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{meeting_data.get('id')}",
        "summary": "A high-level overview focused on the project's critical health path.",
        "category": ["Issue", "Risk", "Dependency", "Decision", "Assumption"],
        "sentiment": "negative | positive | neutral",
        "raiddAnalysis": {{
            "risks": ["A paragraph explaining the future impact of delayed testing or planning."] or null,
            "issues": ["A paragraph explaining any current technical blockers mentioned."] or null,
            "decisions": ["A paragraph confirming what the team agreed to move forward."] or null,
            "assumptions": ["A paragraph about what the project assumes to be true."] or null,
            "dependencies": ["A paragraph about prerequisite actions before the next phase."] or null
        }}
    }}
    """
    
    return llm_summary(user_prompt)