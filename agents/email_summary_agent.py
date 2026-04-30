import json
from openai import OpenAI
from config.settings import settings
from rag.retriever import retrieve_context

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def run_email_analysis(email_data, projects_context):
    """
    UPGRADED: Supervised Email Intelligence Agent.
    Uses Hybrid RAG (FAISS + Pinecone) to audit emails against project reality.
    """

    # 1. FETCH KNOWLEDGE FROM BOTH LAYERS
    # Layer 1: Global Governance (FAISS)
    global_rules = retrieve_context("EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE", mode="global")
    
    # Layer 2: Specialized Email Intelligence (Pinecone email-agent index)
    specialized_rules = retrieve_context("advanced email patterns, sub-types, and implicit risk detection", mode="email")

    # 2. PREPARE THE "REALITY CHECK"
    # We turn the project context into a string so the AI can see if the email is lying
    reality_summary = ""
    if projects_context:
        reality_summary = "CURRENT PROJECT REALITY (From Backend):\n"
        for proj in projects_context:
            reality_summary += f"- Project: {proj.get('name')} | Status: {proj.get('status')} | Tasks: {len(proj.get('tasks', []))}\n"
    else:
        reality_summary = "No project context available for cross-referencing."

    # 3. THE SYSTEM INSTRUCTION (The "Brain" of the Auditor)
    system_instruction = """
    You are a Senior Project Management Intelligence Auditor. 
    Your task is to perform a highly supervised audit of incoming emails.

    YOUR KNOWLEDGE BASE:
    You have access to two layers of intelligence:
    1. [GLOBAL GOVERNANCE]: General rules for RAIDD categorization.
    2. [SPECIALIZED EMAIL PATTERNS]: Advanced patterns for detecting hidden risks, implicit dependencies, and sub-types (e.g., Technical, Resource, Security).

    YOUR AUDIT PROCESS:
    1. ANALYZE the email content against the provided KNOWLEDGE BASE.
    2. CROSS-REFERENCE: Compare the email's claims against the 'CURRENT PROJECT REALITY'.
    3. DISCREPANCY DETECTION: If an email claims progress but the reality shows overdue tasks/milestones, you MUST flag this as an 'ISSUE' or 'RISK'.
    4. SUB-TYPING: Every RAIDD item must include its specific sub-type (e.g., 'Resource Risk: [description]').

    STRICT OUTPUT RULES:
    - Return a strictly valid JSON object.
    - 'flag' must be 'Red' if there is a discrepancy between the email and reality, or if critical risks are detected.
    - Each RAIDD field must be a LIST OF STRINGS. Each string must be a descriptive paragraph (2-3 sentences).
    """

    # 4. THE USER PROMPT (The "Work Order")
    user_prompt = f"""
    [KNOWLEDGE BASE]
    {global_rules}
    ---
    {specialized_rules}

    [CURRENT PROJECT REALITY]
    {reality_summary}

    [EMAIL TO AUDIT]
    Subject: {email_data.get('subject')}
    Body: {email_data.get('body')}
    Sender: {email_data.get('from_name', 'Unknown')}

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{email_data.get('id')}",
        "summary": "🔹 [Summary text including if the email aligns with or contradicts project reality]",
        "category": ["Issue", "Risk", "Dependency", "Decision", "Assumption", "Informational"],
        "sentiment": "positive | negative | neutral",
        "raiddAnalysis": {{
            "risks": ["Sub-type: [Type] - [Impact description]"],
            "issues": ["Sub-type: [Type] - [Impact description]"],
            "decisions": ["[Decision description]"],
            "assumptions": ["[Assumption description]"],
            "dependencies": ["[Dependency description]"]
        }}
    }}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"LLM Error on email {email_data.get('id')}: {e}")
        return None