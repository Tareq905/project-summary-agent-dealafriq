import json
from openai import OpenAI
from config.settings import settings
from rag.retriever import retrieve_context

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def run_email_analysis(email_data, projects_context):
    """
    Email Intelligence Agent.
    Uses email-agent-v2 (Pinecone, multilingual-e5-large, 1024 dims) as primary RAIDD knowledge.
    Falls back to FAISS global governance for structural rules.
    """

    # ── 1. RAG RETRIEVAL ─────────────────────────────────────
    global_rules = retrieve_context(
        "EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE",
        mode="global"
    )

    email_raidd_knowledge = retrieve_context(
        "RAIDD risk issue assumption decision dependency email detection patterns action items next steps",
        mode="email"
    )

    # ── 2. PROJECT REALITY CHECK ─────────────────────────────
    reality_summary = ""
    if projects_context:
        reality_summary = "CURRENT PROJECT REALITY (From Backend):\n"
        for proj in projects_context:
            reality_summary += (
                f"- Project: {proj.get('name')} | "
                f"Status: {proj.get('status')} | "
                f"Tasks: {len(proj.get('tasks', []))}\n"
            )
    else:
        reality_summary = "No project context available for cross-referencing."

    # ── 3. SYSTEM INSTRUCTION ────────────────────────────────
    system_instruction = """
    You are a Senior Project Management Intelligence Auditor specializing in RAIDD detection from emails.

    YOUR KNOWLEDGE BASE PRIORITY:
    1. [PRIMARY RAIDD KNOWLEDGE — Client Trained]: Your main detection reference.
       Use the patterns, definitions, and examples from this layer first.
    2. [GLOBAL GOVERNANCE]: Structural rules for output formatting.

    YOUR AUDIT PROCESS:
    1. READ the entire email body carefully, sentence by sentence.
    2. DETECT all 5 RAIDD categories — risks, issues, decisions, assumptions, dependencies.
    3. NEVER leave decisions empty if any of these exist in the email:
       - ACTION items assigned to named people
       - "Next step:" statements
       - Approvals needed or requested
       - Go/no-go points
       - Change requests being submitted
       - Anything that has been agreed or needs to be confirmed
    4. CROSS-REFERENCE email claims against project reality for discrepancies.
    5. SUB-TYPE every RAIDD item.
    6. GENERATE a professional reply.

    STRICT OUTPUT RULES:
    - Return strictly valid JSON only.
    - Each RAIDD field MUST be a LIST OF STRINGS.
    - decisions MUST NEVER be empty if action items, next steps, or approvals exist in the email.
    - generatedReply must never be null or empty.
    """

    # ── 4. USER PROMPT ───────────────────────────────────────
    user_prompt = f"""
    [PRIMARY RAIDD KNOWLEDGE — Client Trained Documents]
    {email_raidd_knowledge}

    [GLOBAL GOVERNANCE RULES]
    {global_rules}

    [CURRENT PROJECT REALITY]
    {reality_summary}

    [EMAIL TO AUDIT]
    Subject: {email_data.get('subject')}
    Body: {email_data.get('body')}
    Sender: {email_data.get('from_name', 'Unknown')}

    ══════════════════════════════════════════════════════
    RAIDD DETECTION RULES — MANDATORY. READ EVERY LINE.
    ══════════════════════════════════════════════════════

    - risks:
      Detect: technical failures, resource threats, timeline risks, security concerns,
      performance issues, compliance gaps, third-party risks, scope creep.
      Trigger phrases: "at risk", "concern", "worried", "could fail", "may impact",
      "single point of failure", "no knowledge transfer", "unvetted", "bypassed".

    - issues:
      Detect: current active blockers, bugs, failures, unresolved problems,
      SLA breaches, system errors, audit failures.
      Trigger phrases: "failing", "error", "unresolved", "intermittent", "exceeds SLA",
      "not provided an ETA", "discrepancy", "misconfigured", "pending for X days/weeks".

    - decisions:
      ⚠️ THIS IS CRITICAL — DO NOT LEAVE EMPTY IF ANY OF THESE EXIST:
      - "ACTION (name):" → this is a decision/assigned action — MUST be captured
      - "Next step:" → this is a decision about what happens next — MUST be captured
      - "We will..." → committed decision — MUST be captured
      - "needs to complete", "needs to compile", "needs to schedule" → assigned decisions
      - "pending approval", "submit the change request", "written confirmation needed"
      - "CAB approval", "change control", "sign-off", "confirm with"
      Every ACTION item and every Next Step in this email is a decision. Capture ALL of them.

    - assumptions:
      Detect: unvalidated expectations, things taken for granted, implied agreements.
      Trigger phrases: "assuming", "will be sufficient", "typically takes", "expected",
      "I believe", "should be ready", "outside our control".

    - dependencies:
      Detect: waiting-on relationships, blocked-by chains, prerequisite tasks,
      external blockers, third-party dependencies.
      Trigger phrases: "depends on", "dependent on", "waiting for", "pending from",
      "before we can", "request submitted", "need X before Y".

    ══════════════════════════════════════════════════════
    STRICT RULES FOR ALL CATEGORIES:
    ══════════════════════════════════════════════════════
    - Each item MUST include sub-type prefix: e.g., "Action Decision: ...", "Resource Risk: ..."
    - Each item MUST be 2-3 sentences — specific, factual, grounded in the email.
    - Reference actual names (Grace, Carlos, Kate, Chloe), systems, dates, numbers from email.
    - Do NOT write generic statements.
    - decisions MUST have at least 3-4 items for this email — there are multiple ACTION items
      and Next Steps explicitly listed.

    ══════════════════════════════════════════════════════
    SUMMARY RULES — MANDATORY
    ══════════════════════════════════════════════════════
    - MUST start with 🔹
    - Intelligence brief style — dense with facts, zero filler.
    - Include: WHO sent it, WHAT risks/issues/decisions were raised, WHAT action is pending.
    - Reference actual names, numbers, systems, dates.
    - Length: 2-3 sentences max.

    ══════════════════════════════════════════════════════
    GENERATED REPLY RULES — MANDATORY
    ══════════════════════════════════════════════════════
    - Address sender by name.
    - Acknowledge key points raised.
    - Provide clear next steps.
    - Professional tone, 3-5 sentences.
    - NEVER return null or empty string.

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{email_data.get('id')}",
        "summary": "🔹 [Specific, fact-dense intelligence brief]",
        "category": ["Issue", "Risk", "Dependency", "Decision", "Assumption", "Informational"],
        "sentiment": "positive | negative | neutral",
        "generatedReply": "Professional reply to the email.",
        "raiddAnalysis": {{
            "risks":        ["Sub-type: [Type] — [2-3 sentence description]"],
            "issues":       ["Sub-type: [Type] — [2-3 sentence description]"],
            "decisions":    ["Sub-type: [Type] — [2-3 sentence description]"],
            "assumptions":  ["Sub-type: [Type] — [2-3 sentence description]"],
            "dependencies": ["Sub-type: [Type] — [2-3 sentence description]"]
        }}
    }}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user",   "content": user_prompt}
            ]
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"LLM Error on email {email_data.get('id')}: {e}")
        return None