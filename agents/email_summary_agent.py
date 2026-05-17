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
    global_rules      = retrieve_context("EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE", mode="global")
    specialized_rules = retrieve_context("advanced email patterns, sub-types, and implicit risk detection", mode="email")

    # 2. PREPARE THE "REALITY CHECK"
    reality_summary = ""
    if projects_context:
        reality_summary = "CURRENT PROJECT REALITY (From Backend):\n"
        for proj in projects_context:
            reality_summary += f"- Project: {proj.get('name')} | Status: {proj.get('status')} | Tasks: {len(proj.get('tasks', []))}\n"
    else:
        reality_summary = "No project context available for cross-referencing."

    # 3. SYSTEM INSTRUCTION
    system_instruction = """
    You are a Senior Project Management Intelligence Auditor. 
    Your task is to perform a highly supervised audit of incoming emails AND generate a professional reply.

    YOUR KNOWLEDGE BASE:
    You have access to two layers of intelligence:
    1. [GLOBAL GOVERNANCE]: General rules for RAIDD categorization.
    2. [SPECIALIZED EMAIL PATTERNS]: Advanced patterns for detecting hidden risks, implicit dependencies, and sub-types (e.g., Technical, Resource, Security).

    YOUR AUDIT PROCESS:
    1. ANALYZE the email content against the provided KNOWLEDGE BASE.
    2. CROSS-REFERENCE: Compare the email's claims against the 'CURRENT PROJECT REALITY'.
    3. DISCREPANCY DETECTION: If an email claims progress but the reality shows overdue tasks/milestones, flag this as an 'ISSUE' or 'RISK'.
    4. SUB-TYPING: Every RAIDD item must include its specific sub-type (e.g., 'Resource Risk: [description]').
    5. GENERATED REPLY: Draft a professional, context-aware reply to the email sender addressing their concerns.

    STRICT OUTPUT RULES:
    - Return a strictly valid JSON object.
    - 'flag' must be 'Red' if there is a discrepancy between the email and reality, or if critical risks are detected.
    - Each RAIDD field must be a LIST OF STRINGS. Each string must be a descriptive paragraph (2-3 sentences).
    - 'generatedReply' must be a professional email reply string. Address the sender by name if available. 
      Acknowledge their concerns, provide reassurance or next steps, and sign off professionally.
    """

    # 4. USER PROMPT
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

    RAIDD DETECTION RULES (MANDATORY):
    - risks: Technical, compliance, architectural, performance risks mentioned or implied.
    - issues: Current blockers, bugs, failures, unresolved problems.
    - decisions: Any decision made, agreed upon, or requested in the email.
    - assumptions: Anything the sender assumes to be true without confirmation.
    - dependencies: Any prerequisite, waiting-on, or blocked-by relationship mentioned.
    - Every category MUST have at least 1 item if the email content justifies it.
    - Do NOT leave decisions, assumptions, or dependencies empty if they can be inferred.

    SUMMARY RULES (MANDATORY):
    - The summary MUST start with 🔹
    - The summary MUST be specific and informative — written like an intelligence brief.
    - Include: WHO sent it, WHAT specific issues/risks/decisions were raised, and WHAT action is pending.
    - Mention actual names, numbers, systems, or project details from the email body.
    - Do NOT write generic statements like "critical risks impacting delivery" or "immediate action required".
    - Example of BAD summary: "🔹 The email highlights critical risks and issues impacting project delivery."
    - Example of GOOD summary: "🔹 Robert flagged that 2,300 records failed migration due to encoding issues,
      LTIMindtree's lead consultant may be reassigned affecting UAT support, and two senior developers risk
      being pulled to other projects. A go/no-go decision for UAT is pending Monday's status meeting."
    - Length: 2-3 sentences maximum. Dense with facts, zero filler.

    GENERATED REPLY RULES (MANDATORY):
    - You MUST generate a professional reply to this email.
    - The reply should acknowledge the key points and provide next steps.
    - Reply must be 3-5 sentences, professional tone.
    - NEVER return null or empty string for generatedReply.

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{email_data.get('id')}",
        "summary": "🔹 [Specific, fact-dense summary of the email]",
        "category": ["Issue", "Risk", "Dependency", "Decision", "Assumption", "Informational"],
        "sentiment": "positive | negative | neutral",
        "generatedReply": "Professional reply to the email here.",
        "raiddAnalysis": {{
            "risks": ["Sub-type: [Type] - [2-3 sentence impact description]"],
            "issues": ["Sub-type: [Type] - [2-3 sentence impact description]"],
            "decisions": ["[Decision description - what was decided or needs to be decided]"],
            "assumptions": ["[Assumption description - what is being assumed]"],
            "dependencies": ["[Dependency description - what depends on what]"]
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