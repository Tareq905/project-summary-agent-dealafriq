import json
from openai import OpenAI
from config.settings import settings
from rag.retriever import retrieve_context

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def run_email_analysis(email_data, projects_context):
    """
    Email Intelligence Agent.
    Extracts 7 categories per training data:
    Risks, Issues, Dependencies, Assumptions, Tasks, Actions, Next Steps.
    Uses email-agent-v2 (Pinecone, multilingual-e5-large, 1024 dims).
    """

    # ── 1. RAG RETRIEVAL ─────────────────────────────────────
    global_rules = retrieve_context(
        "EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE",
        mode="global"
    )

    email_raidd_knowledge = retrieve_context(
        "RAIDD risk issue assumption decision dependency task action next step email extraction patterns",
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
    You are a Senior Project Management Intelligence Auditor trained to extract
    exactly 7 categories from project management emails.

    THE 7 EXTRACTION CATEGORIES (from training data):
    1. risks       - Potential future problems, threats, uncertainties
    2. issues      - Current active problems, blockers, failures
    3. dependencies - Waiting-on relationships, prerequisites, blocked-by chains
    4. assumptions  - Things taken for granted, unvalidated expectations
    5. tasks        - Work items assigned to people or teams (e.g. "X needs to do Y")
    6. actions      - Explicit ACTION items assigned to named individuals (e.g. "ACTION (Name):")
    7. nextSteps    - "Next step:" statements about what happens next

    CRITICAL DISTINCTION:
    - tasks: "[Person/Team] needs to [do something]" or "[Person] is tasked with..."
    - actions: Starts with "ACTION (Name):" — explicitly labelled action items
    - nextSteps: Starts with "Next step:" — explicitly labelled next steps
    - These are THREE SEPARATE categories. NEVER mix them together.

    STRICT OUTPUT RULES:
    - Return strictly valid JSON only.
    - All 7 fields must be present even if empty list.
    - Each item must be the EXACT extracted text from the email — not a paraphrase.
    - actions MUST only contain items explicitly prefixed with "ACTION (Name):"
    - nextSteps MUST only contain items explicitly prefixed with "Next step:"
    - tasks are work items WITHOUT the ACTION or Next step prefix.
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
    EXTRACTION RULES — READ THE EMAIL SENTENCE BY SENTENCE
    ══════════════════════════════════════════════════════

    1. RISKS — Extract potential future threats/problems:
       Signals: "risk", "could", "may", "might", "concerned about",
       "potential", "at risk", "if X then Y", "impact", "threat",
       "flagged a risk", "there is a risk that"

    2. ISSUES — Extract current active problems/blockers:
       Signals: "issue", "problem", "failed", "failing", "blocked",
       "unavailable", "error", "unresolved", "breach", "cannot proceed",
       "has been raised", "remains unresolved", "critical issue"

    3. DEPENDENCIES — Extract waiting-on / blocked-by relationships:
       Signals: "dependent on", "depends on", "waiting for",
       "before we can", "cannot proceed until", "is a dependency",
       "requires X from Y", "outside our control"

    4. ASSUMPTIONS — Extract things taken for granted:
       Signals: "assuming", "we assume", "the plan assumes",
       "assumes that", "based on the assumption", "expected to",
       "assuming that X will", "on the basis that"

    5. TASKS — Extract work items assigned to people/teams:
       Signals: "[Person] needs to", "[Team] needs to",
       "[Person] is tasked with", "we need to [do X]",
       "[Name] needs to [verb]", "[Role] needs to complete"
       NOTE: Do NOT include items that start with "ACTION" or "Next step"

    6. ACTIONS — Extract ONLY explicit ACTION items:
       Pattern: "ACTION (Name): [description]"
       Extract the FULL text including "ACTION (Name):" prefix.
       ONLY items explicitly labelled as ACTION count here.

    7. NEXT STEPS — Extract ONLY explicit Next Step items:
       Pattern: "Next step: [description]"
       Extract the FULL text including "Next step:" prefix.
       ONLY items explicitly labelled as "Next step:" count here.

    ══════════════════════════════════════════════════════
    SUMMARY RULES
    ══════════════════════════════════════════════════════
    - MUST start with 🔹
    - Dense with facts — WHO sent it, WHAT was flagged, WHAT action pending
    - Reference actual names, numbers, systems from the email
    - 2-3 sentences max

    ══════════════════════════════════════════════════════
    GENERATED REPLY RULES
    ══════════════════════════════════════════════════════
    - Address sender by name
    - Acknowledge key points
    - Provide next steps
    - Professional tone, 3-5 sentences
    - NEVER null or empty

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{email_data.get('id')}",
        "summary": "🔹 [fact-dense intelligence brief]",
        "category": ["Risk", "Issue", "Dependency", "Assumption", "Task", "Action", "NextStep"],
        "sentiment": "positive | negative | neutral",
        "generatedReply": "Professional reply.",
        "raiddAnalysis": {{
            "risks":        ["exact extracted text from email"],
            "issues":       ["exact extracted text from email"],
            "dependencies": ["exact extracted text from email"],
            "assumptions":  ["exact extracted text from email"],
            "tasks":        ["exact extracted text from email"],
            "actions":      ["ACTION (Name): exact extracted text"],
            "nextSteps":    ["Next step: exact extracted text"]
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