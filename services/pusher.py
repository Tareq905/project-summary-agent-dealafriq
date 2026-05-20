import requests
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "x-backend-service": settings.BACKEND_SERVICE_SECRET,
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}


def _post(url: str, payload: dict, label: str) -> bool:
    logger.info(f"[{label}] Pushing to URL: {url}")
    logger.info(f"[{label}] Payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=30)
        logger.info(f"[{label}] Response Status: {response.status_code}")
        logger.info(f"[{label}] Response Body: {response.text}")
        if response.status_code in (200, 201):
            logger.info(f"{label} pushed successfully.")
            return True
        else:
            logger.error(f"{label} push failed: {response.status_code} — {response.text}")
            return False
    except Exception as e:
        logger.error(f"{label} push exception: {e}")
        return False


# ── 1. Project AI Summary ─────────────────────────────────
def push_project_summary(
    project_id: str,
    ai_summary: str,
    project_progress: str,
    project_health: str,
    notes: str = "",
    discussion_points: list = None,
    action_points: list = None,
    raidd_data: dict = None
):
    health_color_map = {
        "excellent": "green",
        "good":      "amber",
        "bad":       "red",
    }
    health_color = health_color_map.get((project_health or "").lower(), "red")

    url = f"{settings.AI_UPDATE_PROJECT_API}/{project_id}"
    payload = {
        "projectAiSummary": ai_summary,
        "projectProgress":  project_progress,
        "projectHealth":    health_color,
        "notes":            notes,
        "discussionPoints": discussion_points or [],
        "actionPoints":     action_points or [],
        "raiddData":        raidd_data or {
            "risks": [], "issues": [], "assumptions": [], "dependencies": [], "decisions": []
        }
    }
    return _post(url, payload, f"Project[{project_id}]")


# ── 2. Weekly Summary ─────────────────────────────────────
def push_weekly_summary(project_id: str, weekly_summary: str):
    url = f"{settings.AI_UPDATE_WEEKLY_SUMMARY_API}/{project_id}"
    payload = {
        "weeklyAiSummary": weekly_summary
    }
    return _post(url, payload, f"WeeklySummary[{project_id}]")


# ── 3. Meeting AI Result ──────────────────────────────────
def push_meeting_result(
    meeting_id: str,
    notes: str,
    agenda: str,
    key_points,       
    action_points,
    raidd_flags: dict = None,
    ai_meeting_summary: str = None  
):
    url = f"{settings.AI_UPDATE_MEETING_API}/{meeting_id}"
    raidd = raidd_flags or {}

    payload = {
        "notes":            notes,
        "agenda":           agenda,
        "aiMeetingSummary": ai_meeting_summary,
        "raiddData": {
            "risks":        [{"data": d} for d in raidd.get("risks", [])        if d],
            "issues":       [{"data": d} for d in raidd.get("issues", [])       if d],
            "assumptions":  [{"data": d} for d in raidd.get("assumptions", [])  if d],
            "dependencies": [{"data": d} for d in raidd.get("dependencies", []) if d],
            "decisions":    [{"data": d} for d in raidd.get("decisions", [])    if d],
        }
    }

    if isinstance(key_points, dict):
        payload["keyPoints"] = key_points
    elif isinstance(key_points, list) and key_points:
        payload["keyPoints"] = {
            "deleteMany": {},
            "create": [{"content": str(k)} for k in key_points if k]
        }

    if isinstance(action_points, dict):
        payload["actionPoints"] = action_points
    elif isinstance(action_points, list) and action_points:
        payload["actionPoints"] = {
            "deleteMany": {},
            "create": [{"content": str(a)} for a in action_points if a]
        }

    return _post(url, payload, f"Meeting[{meeting_id}]")


# ── 4. Document AI Result ─────────────────────────────────
def push_document_result(document_id: str, ai_summary: str, key_points, action_points):
    url = f"{settings.AI_UPDATE_DOCUMENT_API}/{document_id}"

    payload = {
        "aiDocumentSummary": ai_summary,
    }

    if isinstance(key_points, dict):
        payload["keyPoints"] = key_points
    elif isinstance(key_points, list) and key_points:
        payload["keyPoints"] = {
            "deleteMany": {},
            "create": [{"content": str(k)} for k in key_points if k]
        }

    if isinstance(action_points, dict):
        payload["actionPoints"] = action_points
    elif isinstance(action_points, list) and action_points:
        payload["actionPoints"] = {
            "deleteMany": {},
            "create": [{"content": str(a)} for a in action_points if a]
        }

    return _post(url, payload, f"Document[{document_id}]")


# ── 5. Email AI Result ────────────────────────────────────
def push_email_result(email_id: str, summary: str, tasks: list, raidd_category: list, raidd_data: dict, generated_reply: str = ""):
    url = f"{settings.AI_UPDATE_EMAIL_API}/{email_id}"

    payload = {
        "raiddMessage":        summary,
        "raiddCategory":       raidd_category,
        "generatedReply":      generated_reply,
        "sentiment":           None,
        "projectRisks":        [{"data": d["data"]} for d in raidd_data.get("risks", [])        if d],
        "projectIssues":       [{"data": d["data"]} for d in raidd_data.get("issues", [])       if d],
        "projectAssumptions":  [{"data": d["data"]} for d in raidd_data.get("assumptions", [])  if d],
        "projectDecisions":    [{"data": d["data"]} for d in raidd_data.get("decisions", [])    if d],
        "projectDependencies": [{"data": d["data"]} for d in raidd_data.get("dependencies", []) if d],
    }

    for key in ["projectRisks", "projectIssues", "projectAssumptions", "projectDecisions", "projectDependencies"]:
        if not payload[key]:
            del payload[key]

    return _post(url, payload, f"Email[{email_id}]")


# ── 6. AI Detection ───────────────────────────────────────
def push_ai_detection(
    project_id: str,
    project_name: str,
    flag: str,
    health_label: str,
    project_progress: str,
    ai_summary: str,
    action_points: list,
    discussion_points: list,
    notes: str,
    raidd_flags: dict
):
    payload = {
        "projectId":        project_id,
        "projectName":      project_name,
        "flag":             flag,
        "healthLabel":      health_label,
        "projectProgress":  project_progress,
        "aiSummary":        ai_summary,
        "actionPoints":     action_points,
        "discussionPoints": discussion_points,
        "notes":            notes,
        "raiddFlags":       raidd_flags
    }
    return _post(settings.AI_DETECTION_API, payload, f"AIDetection[{project_id}]")

# ── 7. Email Draft ────────────────────────────────────────
# def push_email_draft(
#     email_id: str,
#     draft_subject: str,
#     draft_body: str,
#     intent_tag: str,
#     urgency: str,
#     key_points_addressed: list
# ) -> bool:
#     """
#     Pushes a generated email draft to the backend.
#     Called by email_draft_orchestrator on both first-time generation
#     and regeneration requests.
 
#     :param email_id:             The ID of the original email.
#     :param draft_subject:        The reply subject line.
#     :param draft_body:           The full assembled draft body (ready-to-send string).
#     :param intent_tag:           Classified intent (e.g. "Acknowledgement", "Escalation").
#     :param urgency:              Draft urgency level: "High", "Medium", or "Low".
#     :param key_points_addressed: List of specific concerns addressed in the draft.
#     """
#     url = f"{settings.AI_UPDATE_EMAIL_API}/{email_id}/draft"
 
#     payload = {
#         "emailId":            email_id,
#         "draftSubject":       draft_subject,
#         "draftBody":          draft_body,
#         "intentTag":          intent_tag,
#         "urgency":            urgency,
#         "keyPointsAddressed": key_points_addressed
#     }
 
#     return _post(url, payload, f"EmailDraft[{email_id}]")