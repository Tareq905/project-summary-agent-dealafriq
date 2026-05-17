import json
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def run_client_analysis(client_data: dict) -> dict | None:
    """
    Client Intelligence Agent.
    Analyzes a client's full profile — projects, meetings, emails, documents —
    and generates aiSummary, lessonsLearned, discussionPoints, actionPoints,
    notes, and raiddData.
    """

    # ── Client profile ─────────────────────────────────────
    client_name        = client_data.get("name", "Unknown Client")
    client_email       = client_data.get("email", "")
    contact_person     = client_data.get("contactPerson", "")
    contact_role       = client_data.get("contactRole", "")
    contact_email      = client_data.get("contactEmail", "")
    num_projects       = client_data.get("numberOfProjects", 0)
    meeting_links      = client_data.get("meetingLinks", [])
    slas               = client_data.get("slas", [])

    # ── Projects summary ───────────────────────────────────
    projects = client_data.get("projects", [])
    project_summaries = []
    all_action_points = []
    all_discussion_points = []
    all_notes = []
    all_meetings = []
    all_documents = []

    for proj in projects:
        proj_name     = proj.get("name", "")
        proj_status   = proj.get("status", "")
        proj_health   = proj.get("projectHealth", "")
        proj_progress = proj.get("projectProgress", "0%")
        proj_notes    = proj.get("notes", "")
        proj_desc     = proj.get("description", "")

        if proj_notes:
            all_notes.append(f"[{proj_name}]: {proj_notes}")

        all_action_points.extend(proj.get("actionPoints", []))
        all_discussion_points.extend(proj.get("discussionPoints", []))

        meetings = proj.get("meetings", [])
        for mtg in meetings:
            all_meetings.append({
                "project":    proj_name,
                "title":      mtg.get("title", ""),
                "date":       mtg.get("meetingDate", ""),
                "notes":      mtg.get("notes", ""),
                "agenda":     mtg.get("agenda", ""),
                "summary":    mtg.get("lastMeetingSummary", "")
            })

        docs = proj.get("documents", [])
        for doc in docs:
            all_documents.append({
                "project":  proj_name,
                "fileName": doc.get("fileName", ""),
                "summary":  doc.get("aiDocumentSummary", "")
            })

        project_summaries.append(
            f"- Project: {proj_name} | Status: {proj_status} | "
            f"Health: {proj_health} | Progress: {proj_progress} | "
            f"Description: {proj_desc[:200] if proj_desc else 'N/A'}"
        )

    # ── Emails summary ─────────────────────────────────────
    emails = client_data.get("emails", [])
    email_summaries = []
    for email in emails[:10]:  # cap at 10 to avoid token overflow
        email_summaries.append(
            f"- Subject: {email.get('subject', '')} | "
            f"Body (excerpt): {email.get('body', '')[:300]}"
        )

    # ── Build prompt ───────────────────────────────────────
    system_instruction = """
    You are a Senior Client Intelligence Agent for a Project Management System.
    Your task is to analyze a client's full profile and generate a comprehensive
    intelligence report.

    STRICT OUTPUT RULES:
    - Return a strictly valid JSON object.
    - All list fields must be lists of strings EXCEPT raiddData which has a specific structure.
    - raiddData fields must be lists of objects with a single "data" key: [{"data": "..."}]
    - Be specific and factual. Use client name, project names, and real details.
    - Do NOT be generic. Every insight must be grounded in the provided data.
    """

    user_prompt = f"""
    CLIENT PROFILE:
    Name: {client_name}
    Email: {client_email}
    Contact Person: {contact_person} ({contact_role}) — {contact_email}
    Total Projects: {num_projects}
    Meeting Platforms: {', '.join([m.get('title', '') + ': ' + m.get('link', '') for m in meeting_links]) if meeting_links else 'Not specified'}
    SLAs: {json.dumps(slas) if slas else 'No SLAs recorded'}

    PROJECTS:
    {chr(10).join(project_summaries) if project_summaries else 'No projects found.'}

    RECENT MEETINGS:
    {chr(10).join([f"- [{m['project']}] {m['title']} on {m['date']}: {m['summary'] or m['notes'] or m['agenda'] or 'No content'}" for m in all_meetings]) if all_meetings else 'No meetings found.'}

    DOCUMENTS:
    {chr(10).join([f"- [{d['project']}] {d['fileName']}: {d['summary'] or 'No summary'}" for d in all_documents]) if all_documents else 'No documents found.'}

    EMAILS (Recent):
    {chr(10).join(email_summaries) if email_summaries else 'No emails found.'}

    EXISTING ACTION POINTS FROM PROJECTS:
    {chr(10).join([f"- {a}" for a in all_action_points]) if all_action_points else 'None.'}

    EXISTING DISCUSSION POINTS FROM PROJECTS:
    {chr(10).join([f"- {d}" for d in all_discussion_points]) if all_discussion_points else 'None.'}

    EXISTING NOTES FROM PROJECTS:
    {chr(10).join(all_notes) if all_notes else 'None.'}

    TASK:
    Analyze all the above data and generate a client intelligence report.

    FIELD RULES:

    "aiSummary":
    - 2-3 sentence professional overview of this client.
    - Include: number of projects, overall health, key patterns observed.
    - Be specific — mention project names, health status, recurring themes.

    "lessonsLearned":
    - Extract lessons from patterns across projects, meetings, and emails.
    - Look for: recurring issues, repeated action points, unresolved risks,
      communication patterns, approval delays, documentation gaps.
    - Each lesson must be a specific, actionable insight.
    - Minimum 2-3 lessons. Example:
      "Ensure staging environment access is confirmed before integration testing begins,
       as environment-level dependencies have caused repeated delays for this client."

    "discussionPoints":
    - Key topics that should be discussed in the next client meeting.
    - Derived from unresolved issues, pending decisions, project health.
    - Minimum 2-3 points.

    "actionPoints":
    - Specific actions the team must take for this client.
    - Derived from email requests, meeting outcomes, project blockers.
    - Minimum 2-3 actions.

    "notes":
    - A single string summarizing key contextual information about this client.
    - Include contact preferences, communication style, key risks, SLA priorities.

    "raiddData":
    - Analyze ALL projects, meetings, and emails for RAIDD signals.
    - risks: What could go wrong across this client's projects?
    - issues: What current problems exist?
    - assumptions: What is being assumed without confirmation?
    - decisions: What decisions are pending or have been made?
    - dependencies: What is blocking progress?
    - Each item must be an object: {{"data": "descriptive paragraph"}}
    - Minimum 1 item per category if evidence exists.

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "aiSummary": "string",
        "lessonsLearned": ["string"],
        "discussionPoints": ["string"],
        "actionPoints": ["string"],
        "notes": "string",
        "raiddData": {{
            "risks": [{{"data": "string"}}],
            "issues": [{{"data": "string"}}],
            "assumptions": [{{"data": "string"}}],
            "decisions": [{{"data": "string"}}],
            "dependencies": [{{"data": "string"}}]
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
        print(f"❌ Client Agent LLM Error for {client_name}: {e}")
        return None