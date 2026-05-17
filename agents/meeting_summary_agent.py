from utils.llm_client import llm_meeting_summary
from rag.retriever import retrieve_context


def run_meeting_summary(mtg, transcript_list):
    context = retrieve_context("CLIENT_SUMMARY_STYLE meeting patterns RAIDD extraction")

    # ── Build transcript text ──────────────────────────────
    transcript_text = ""
    if transcript_list:
        for t in transcript_list:
            speeches = t.get("parsedData", {}).get("speeches", [])
            transcript_text += " ".join([
                f"{s.get('speaker')}: {s.get('message')}"
                for s in speeches if s.get("message")
            ])

    # ── Meeting fields ─────────────────────────────────────
    mtg_date      = mtg.get("meetingDate") or mtg.get("createdAt") or "Unknown Date"
    key_points    = mtg.get("keyPoints", [])
    action_points = mtg.get("actionPoints", [])
    notes         = mtg.get("notes", "")
    title         = mtg.get("title", "Unknown Meeting")

    project      = mtg.get("project", {}) or {}
    project_name = project.get("name", "")
    project_desc = project.get("description", "")

    kp_text = "\n".join([f"- {kp.get('content', '')}" for kp in key_points]) if key_points else ""
    ap_text = "\n".join([f"- {ap.get('content', '')}" for ap in action_points]) if action_points else ""

    # ── Determine what data is available ──────────────────
    has_transcript    = bool(transcript_text.strip())
    has_notes         = bool(notes.strip())
    has_key_points    = bool(kp_text.strip())
    has_action_points = bool(ap_text.strip())
    has_rich_data     = has_transcript or has_notes or has_key_points or has_action_points

    prompt = f"""
    Style Guidelines:
    {context}

    MEETING DATA:
    Title: {title}
    Date: {mtg_date}
    Project: {project_name}
    Project Description: {project_desc or "Not provided."}
    Notes: {notes if has_notes else "None."}
    Key Points: {kp_text if has_key_points else "None."}
    Action Points: {ap_text if has_action_points else "None."}

    TRANSCRIPT:
    {transcript_text[:7000] if has_transcript else "None."}

    HAS RICH DATA: {has_rich_data}

    TASK:
    Analyze the meeting data above and return a structured JSON summary.

    CONTENT GENERATION RULES:

    IF "HAS RICH DATA" IS TRUE (transcript, notes, or key/action points exist):
    - "aiMeetingSummary": Write a detailed professional summary from the available content.
    - "agenda": Extract as a plain string if agenda items are present. Otherwise null.
    - "notes": Summarize the notes content as a string. Otherwise null.
    - "keyPoints": Extract key discussion points as a list of strings from the content.
    - "actionPoints": Extract action items as a list of strings from the content.

    IF "HAS RICH DATA" IS FALSE (only title, date, project name, and description available):
    - "aiMeetingSummary": Write a 2-3 sentence professional summary based on the meeting title
      and project context. Describe what this type of meeting typically covers for this project.
    - "agenda": Generate a brief agenda string based on the meeting title and project description.
    - "notes": Generate 2-3 sentences of contextual notes based on the meeting title and project.
    - "keyPoints": Generate 2-3 relevant key points inferred from the meeting title and project description.
    - "actionPoints": Generate 2-3 logical action items inferred from the meeting title and project context.

    RAIDD DETECTION RULES — ALWAYS APPLY REGARDLESS OF DATA AVAILABILITY:
    You MUST analyze all available context (title, project name, description, notes, transcript,
    key points, action points) and populate RAIDD flags wherever logically applicable.

    - "risks": What could go wrong based on this meeting's purpose or project context?
      Example: client misalignment, unclear deliverables, resource constraints.
    - "assumptions": What is being assumed as true for this meeting or project to proceed?
      Example: client availability, agreed scope, budget approval.
    - "issues": What current problems or blockers are implied by the meeting title or content?
      Example: unresolved client feedback, pending decisions, stalled progress.
    - "dependencies": What does progress depend on after this meeting?
      Example: client sign-off, team availability, third-party input.
    - "decisions": What decisions need to be made or were made in this meeting context?
      Example: project direction, resource allocation, timeline confirmation.

    RAIDD STRICT RULES:
    - You MUST populate at least 2-3 RAIDD items across the categories based on the meeting
      title, project name, and description — even if no transcript or notes exist.
    - Each RAIDD item MUST be a 2-3 sentence descriptive paragraph.
    - Do NOT return all empty lists. At minimum risks, assumptions, and dependencies
      must have at least 1 item each based on the meeting and project context.

    REQUIRED JSON OUTPUT:
    {{
      "aiMeetingSummary": "string",
      "agenda": "string or null",
      "notes": "string or null",
      "keyPoints": ["string"],
      "actionPoints": ["string"],
      "raidd_flags": {{
          "risks": ["2-3 sentence paragraph"],
          "assumptions": ["2-3 sentence paragraph"],
          "issues": ["2-3 sentence paragraph"],
          "dependencies": ["2-3 sentence paragraph"],
          "decisions": ["2-3 sentence paragraph"]
      }}
    }}
    """

    result = llm_meeting_summary(prompt)

    if not result:
        return None

    return result