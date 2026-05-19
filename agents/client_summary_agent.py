import json
import traceback
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ════════════════════════════════════════════════════════════
# DIAGNOSTIC HELPERS
# ════════════════════════════════════════════════════════════

def _dbg(msg: str):
    """Diagnostic print — easy to find in logs."""
    print(f"🔬 [CLIENT_AGENT_DBG] {msg}")


def _inspect(name: str, value):
    """Print field name, type, and a short sample of its content."""
    t = type(value).__name__
    sample = str(value)[:150].replace("\n", " ")
    _dbg(f"  field='{name}' | type={t} | sample={sample!r}")


def _inspect_list_items(name: str, value):
    """Show each item's type inside a list — for spotting str-in-list."""
    if not isinstance(value, list):
        _dbg(f"  LIST_INSPECT '{name}' SKIPPED (not a list, got {type(value).__name__})")
        return
    _dbg(f"  LIST_INSPECT '{name}' — total items: {len(value)}")
    for i, item in enumerate(value):
        t = type(item).__name__
        sample = str(item)[:100].replace("\n", " ")
        _dbg(f"     [{i}] type={t} | sample={sample!r}")


# ════════════════════════════════════════════════════════════
# SAFE LIST PARSING
# ════════════════════════════════════════════════════════════

def _safe_list(value) -> list:
    """
    Accepts multiple data shapes and always returns a clean list of parsed objects.
    """
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("["):
            try:
                value = json.loads(stripped)
            except (json.JSONDecodeError, ValueError):
                return []
        else:
            return []

    if not isinstance(value, list):
        return []

    result = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    result.append(json.loads(stripped))
                    continue
                except (json.JSONDecodeError, ValueError):
                    pass
        result.append(item)
    return result


def _format_meeting_links(meeting_links: list) -> str:
    """Handles both dict-list and string-list formats."""
    if not meeting_links:
        return "Not specified"

    parts = []
    for m in meeting_links:
        if isinstance(m, dict):
            title = m.get("title", "Meeting")
            link  = m.get("link", "")
            parts.append(f"{title}: {link}")
        elif isinstance(m, str):
            parts.append(m)
    return ", ".join(parts) if parts else "Not specified"


# ════════════════════════════════════════════════════════════
# MAIN AGENT — WRAPPED IN FULL DIAGNOSTICS
# ════════════════════════════════════════════════════════════

def run_client_analysis(client_data: dict) -> dict | None:
    """
    Client Intelligence Agent — with full diagnostic instrumentation.
    Every step is logged so we can pinpoint exactly where it crashes.
    """

    # ── STEP 0: ENTRY POINT ──────────────────────────────────
    _dbg("═" * 56)
    _dbg("STEP 0: run_client_analysis ENTERED")
    _dbg(f"  Received argument type: {type(client_data).__name__}")
    _dbg(f"  Received argument preview: {str(client_data)[:200]!r}")

    # ── STEP 1: TYPE NORMALIZATION ───────────────────────────
    if isinstance(client_data, str):
        _dbg("STEP 1: client_data is a STRING — attempting JSON parse")
        try:
            client_data = json.loads(client_data)
            _dbg("STEP 1: JSON parse SUCCESS")
        except (json.JSONDecodeError, ValueError) as e:
            _dbg(f"STEP 1: JSON parse FAILED — {e}")
            return None

    if not isinstance(client_data, dict):
        _dbg(f"STEP 1: client_data is NOT a dict (got {type(client_data).__name__}) — returning None")
        return None

    # ── STEP 2: TOP-LEVEL KEY INSPECTION ─────────────────────
    _dbg("STEP 2: Top-level keys present in client_data:")
    for key in client_data.keys():
        _inspect(key, client_data[key])

    try:
        # ── STEP 3: CLIENT PROFILE FIELDS ────────────────────
        _dbg("STEP 3: Extracting client profile fields...")
        client_name    = client_data.get("name", "Unknown Client")
        client_email   = client_data.get("email", "")
        contact_person = client_data.get("contactPerson", "")
        contact_role   = client_data.get("contactRole", "")
        contact_email  = client_data.get("contactEmail", "")
        num_projects   = client_data.get("numberOfProjects", 0)
        _dbg(f"STEP 3: SUCCESS — client_name='{client_name}', num_projects={num_projects}")

        # ── STEP 4: MEETING LINKS ────────────────────────────
        _dbg("STEP 4: Processing meetingLinks...")
        raw_meeting_links = client_data.get("meetingLinks")
        _inspect("meetingLinks (raw)", raw_meeting_links)
        meeting_links = _safe_list(raw_meeting_links)
        _inspect_list_items("meetingLinks (after _safe_list)", meeting_links)
        _dbg("STEP 4: SUCCESS")

        # ── STEP 5: SLAs ─────────────────────────────────────
        _dbg("STEP 5: Processing slas...")
        raw_slas = client_data.get("slas")
        _inspect("slas (raw)", raw_slas)
        slas = _safe_list(raw_slas)
        _inspect_list_items("slas (after _safe_list)", slas)
        _dbg("STEP 5: SUCCESS")

        # ── STEP 6: PROJECTS ─────────────────────────────────
        _dbg("STEP 6: Processing projects...")
        raw_projects = client_data.get("projects")
        _inspect("projects (raw)", raw_projects)
        projects = _safe_list(raw_projects)
        _inspect_list_items("projects (after _safe_list)", projects)

        project_summaries     = []
        all_action_points     = []
        all_discussion_points = []
        all_notes             = []
        all_meetings          = []
        all_documents         = []

        for p_idx, proj in enumerate(projects):
            _dbg(f"STEP 6.{p_idx}: Processing project at index {p_idx}")
            _dbg(f"  → type: {type(proj).__name__}")

            if not isinstance(proj, dict):
                _dbg(f"  → SKIPPED (not a dict, sample: {str(proj)[:100]!r})")
                continue

            _dbg(f"  → project keys: {list(proj.keys())}")

            proj_name     = proj.get("name", "")
            proj_status   = proj.get("status", "")
            proj_health   = proj.get("projectHealth", "")
            proj_progress = proj.get("projectProgress", "0%")
            proj_notes    = proj.get("notes", "")
            proj_desc     = proj.get("description", "")

            _dbg(f"  → name='{proj_name}', status='{proj_status}'")

            if proj_notes:
                all_notes.append(f"[{proj_name}]: {proj_notes}")

            # Action points
            _dbg(f"STEP 6.{p_idx}.a: Processing actionPoints...")
            raw_ap = proj.get("actionPoints")
            _inspect("actionPoints (raw)", raw_ap)
            ap_list = _safe_list(raw_ap)
            _inspect_list_items("actionPoints (after _safe_list)", ap_list)
            all_action_points.extend(ap_list)

            # Discussion points
            _dbg(f"STEP 6.{p_idx}.b: Processing discussionPoints...")
            raw_dp = proj.get("discussionPoints")
            _inspect("discussionPoints (raw)", raw_dp)
            dp_list = _safe_list(raw_dp)
            _inspect_list_items("discussionPoints (after _safe_list)", dp_list)
            all_discussion_points.extend(dp_list)

            # Meetings
            _dbg(f"STEP 6.{p_idx}.c: Processing meetings...")
            raw_mtgs = proj.get("meetings")
            _inspect("meetings (raw)", raw_mtgs)
            mtgs_list = _safe_list(raw_mtgs)
            _inspect_list_items("meetings (after _safe_list)", mtgs_list)
            for m_idx, mtg in enumerate(mtgs_list):
                _dbg(f"    meeting[{m_idx}] type={type(mtg).__name__}")
                if not isinstance(mtg, dict):
                    _dbg(f"    → SKIPPED (not a dict)")
                    continue
                all_meetings.append({
                    "project": proj_name,
                    "title":   mtg.get("title", ""),
                    "date":    mtg.get("meetingDate", ""),
                    "notes":   mtg.get("notes", ""),
                    "agenda":  mtg.get("agenda", ""),
                    "summary": mtg.get("lastMeetingSummary", "")
                })

            # Documents
            _dbg(f"STEP 6.{p_idx}.d: Processing documents...")
            raw_docs = proj.get("documents")
            _inspect("documents (raw)", raw_docs)
            docs_list = _safe_list(raw_docs)
            _inspect_list_items("documents (after _safe_list)", docs_list)
            for d_idx, doc in enumerate(docs_list):
                _dbg(f"    document[{d_idx}] type={type(doc).__name__}")
                if not isinstance(doc, dict):
                    _dbg(f"    → SKIPPED (not a dict)")
                    continue
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
        _dbg("STEP 6: SUCCESS (all projects processed)")

        # ── STEP 7: EMAILS ───────────────────────────────────
        _dbg("STEP 7: Processing emails...")
        raw_emails = client_data.get("emails")
        _inspect("emails (raw)", raw_emails)
        emails = _safe_list(raw_emails)
        _inspect_list_items("emails (after _safe_list, first 3 only)", emails[:3])
        _dbg(f"  Total emails after parse: {len(emails)}")

        email_summaries = []
        for e_idx, email in enumerate(emails[:10]):
            _dbg(f"STEP 7.{e_idx}: email type={type(email).__name__}")
            if not isinstance(email, dict):
                _dbg(f"  → SKIPPED (not a dict, sample: {str(email)[:80]!r})")
                continue
            subject = email.get("subject", "")
            body    = email.get("body", "")
            email_summaries.append(
                f"- Subject: {subject} | "
                f"Body (excerpt): {body[:300] if isinstance(body, str) else str(body)[:300]}"
            )
        _dbg("STEP 7: SUCCESS")

        # ── STEP 8: BUILD PROMPT ─────────────────────────────
        _dbg("STEP 8: Building prompt...")
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
        Meeting Platforms: {_format_meeting_links(meeting_links)}
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
        - Each lesson must be a specific, actionable insight.
        - Minimum 2-3 lessons.

        "discussionPoints":
        - Key topics for next client meeting.
        - Minimum 2-3 points.

        "actionPoints":
        - Specific actions the team must take for this client.
        - Minimum 2-3 actions.

        "notes":
        - A single string summarizing key contextual information about this client.

        "raiddData":
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
        _dbg(f"STEP 8: SUCCESS — prompt length: {len(user_prompt)} chars")

        # ── STEP 9: OPENAI CALL ──────────────────────────────
        _dbg("STEP 9: Calling OpenAI API...")
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user",   "content": user_prompt}
            ]
        )
        _dbg("STEP 9: OpenAI call returned successfully")

        # ── STEP 10: PARSE RESPONSE ──────────────────────────
        _dbg("STEP 10: Parsing OpenAI JSON response...")
        result = json.loads(res.choices[0].message.content)
        _dbg(f"STEP 10: SUCCESS — keys returned: {list(result.keys())}")
        _dbg(f"✅ COMPLETED analysis for client '{client_name}'")
        _dbg("═" * 56)
        return result

    except Exception as e:
        # ── CATCH-ALL: PRINT EVERYTHING ──────────────────────
        _dbg("✗" * 56)
        _dbg(f"💥 CRASH inside run_client_analysis")
        _dbg(f"   Exception type: {type(e).__name__}")
        _dbg(f"   Exception message: {e}")
        _dbg(f"   Client name (if reached): {client_data.get('name', 'UNKNOWN') if isinstance(client_data, dict) else 'N/A'}")
        _dbg(f"   FULL TRACEBACK:")
        for line in traceback.format_exc().splitlines():
            _dbg(f"     {line}")
        _dbg("✗" * 56)
        return None