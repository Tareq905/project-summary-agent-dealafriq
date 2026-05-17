import logging
import queue
import threading
from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from agents.weekly_summary_agent import run_weekly_summary
from services.nsl_reasoner import apply_nsl_logic
from services.pusher import (
    push_project_summary,
    push_weekly_summary,
    push_meeting_result,
    push_document_result,
    push_ai_detection,
)

logger = logging.getLogger(__name__)

HEALTH_COLOR_MAP = {
    "excellent": "green",
    "good":      "amber",
    "bad":       "red",
}


def _process_single_project(project: dict, index: int, total: int) -> dict | None:
    p_id   = project.get("id")
    p_name = project.get("name", "Unknown")
    logger.info(f"[{index}/{total}] Processing: '{p_name}'")

    try:
        nsl_res = apply_nsl_logic(project)
        intel   = run_project_summary(project, nsl_res["facts"], project.get("meetings", []))
        score   = run_health_score(project, nsl_res)

        raw_health = intel.get("health_label")
        if isinstance(raw_health, list):
            health_label = raw_health[0] if raw_health else "Bad"
        elif isinstance(raw_health, str) and raw_health.strip():
            health_label = raw_health
        else:
            health_label = "Bad" if (nsl_res.get("overdue_count", 0) > 0 or nsl_res.get("overdue_tasks", 0) > 0) else "Good"

        health_color = HEALTH_COLOR_MAP.get(health_label.lower(), "red")

        ai_summary        = intel.get("summary", "")
        project_progress  = nsl_res.get("progress_str", "0%")
        flag              = intel.get("flag", "Green")
        action_points     = intel.get("action_points", [])
        discussion_points = intel.get("discussion_points", [])
        notes             = intel.get("notes", "")
        raidd_flags       = intel.get("raidd_flags", {
            "risks": [], "issues": [], "assumptions": [], "dependencies": [], "decisions": []
        })

        weekly_raw  = run_weekly_summary(project, [])
        weekly_text = weekly_raw.get("weekly_summary") or weekly_raw.get("summary", "") if isinstance(weekly_raw, dict) else str(weekly_raw)

        raidd_data = {
            "risks":        raidd_flags.get("risks", []),
            "issues":       raidd_flags.get("issues", []),
            "assumptions":  raidd_flags.get("assumptions", []),
            "dependencies": raidd_flags.get("dependencies", []),
            "decisions":    raidd_flags.get("decisions", []),
        }

        push_project_summary(
            project_id        = p_id,
            ai_summary        = ai_summary,
            project_progress  = project_progress,
            project_health    = health_label,
            notes             = notes,
            discussion_points = discussion_points,
            action_points     = action_points,
            raidd_data        = raidd_data
        )
        push_weekly_summary(p_id, weekly_text)
        push_ai_detection(
            project_id=p_id, project_name=p_name, flag=flag,
            health_label=health_color, project_progress=project_progress,
            ai_summary=ai_summary, action_points=action_points,
            discussion_points=discussion_points, notes=notes, raidd_flags=raidd_flags
        )

        logger.info(f"[{index}/{total}] '{p_name}' — pushed successfully.")
        return {
            "summary":          ai_summary,
            "projectProgress":  project_progress,
            "projectHealth":    health_color,
            "notes":            notes,
            "discussionPoints": discussion_points,
            "actionPoints":     action_points,
            "raiddData":        raidd_data,
        }

    except Exception as e:
        logger.error(f"[{index}/{total}] Error '{p_name}': {e}")
        return None


# ── Project Analysis — Queue-based serial ─────────────────
def analyze_all_projects(session_data: dict, project_id: str = None):
    projects = session_data.get("projects", [])

    # Filter to single project if id is provided
    if project_id:
        projects = [p for p in projects if p.get("id") == project_id]
        if not projects:
            logger.warning(f"⚠️ No project found with id: {project_id}")
            return []

    total = len(projects)
    logger.info(f"Queue-based project analysis. Total: {total}")

    if not projects:
        return []

    project_queue = queue.Queue()
    for p in projects:
        project_queue.put(p)

    results      = []
    processed    = 0
    results_lock = threading.Lock()

    def worker():
        nonlocal processed
        while not project_queue.empty():
            try:
                project = project_queue.get(block=False)
            except queue.Empty:
                break
            processed += 1
            result = _process_single_project(project, processed, total)
            if result:
                with results_lock:
                    results.append(result)
            project_queue.task_done()
            logger.info(f"Queue remaining: {project_queue.qsize()}")

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    logger.info(f"Done. {len(results)}/{total} succeeded.")
    return results


# ── Weekly Summary Only ───────────────────────────────────
def analyze_weekly_summaries_only(session_data: dict, project_id: str = None):
    projects = session_data.get("projects", [])

    # Filter to single project if id is provided
    if project_id:
        projects = [p for p in projects if p.get("id") == project_id]
        if not projects:
            logger.warning(f"⚠️ No project found with id: {project_id}")
            return []

    logger.info(f"Weekly summary job. Total: {len(projects)} projects.")
    results = []

    for project in projects:
        p_id   = project.get("id")
        p_name = project.get("name", "Unknown")
        try:
            weekly_raw  = run_weekly_summary(project, [])
            weekly_text = weekly_raw.get("weekly_summary") or weekly_raw.get("summary", "") if isinstance(weekly_raw, dict) else str(weekly_raw)
            push_weekly_summary(p_id, weekly_text)
            results.append({"projectId": p_id, "weeklySummary": weekly_text})
            logger.info(f"Weekly summary pushed for '{p_name}'.")
        except Exception as e:
            logger.error(f"Weekly summary error '{p_name}': {e}")

    logger.info(f"Weekly summary done. {len(results)}/{len(projects)} succeeded.")
    return results


# ── Meeting Analysis ──────────────────────────────────────
def analyze_all_meetings(session_data: dict, meeting_id: str = None):
    projects = session_data.get("projects", [])
    logger.info(f"Meeting analysis...")
    results = []

    for project in projects:
        p_id     = project.get("id")
        p_name   = project.get("name", "Unknown")
        meetings = project.get("meetings", [])

        if not meetings:
            logger.info(f"No meetings for '{p_name}'. Skipping.")
            continue

        # Filter to single meeting if id is provided, otherwise take latest
        if meeting_id:
            target_meetings = [m for m in meetings if m.get("id") == meeting_id]
            if not target_meetings:
                logger.info(f"No meeting with id [{meeting_id}] in project '{p_name}'. Skipping.")
                continue
            latest_meeting = target_meetings[0]
        else:
            latest_meeting = sorted(
                meetings,
                key=lambda x: x.get("meetingDate") or x.get("createdAt") or ""
            )[-1]

        m_id = latest_meeting.get("id")

        try:
            transcripts = latest_meeting.get("transcripts", [])
            intel = run_meeting_summary(latest_meeting, transcripts)

            logger.info(f"DEBUG Meeting AI Response for [{m_id}]: {intel}")

            if intel is None:
                logger.warning(f"Meeting [{m_id}] for '{p_name}' — AI returned None.")
                continue

            # ── Extract fields from agent response ────────
            ai_meeting_summary = intel.get("aiMeetingSummary") or None
            raw_notes          = intel.get("notes") or None
            agenda             = intel.get("agenda") or None
            raw_key_points     = intel.get("keyPoints") or []
            raw_action_points  = intel.get("actionPoints") or []
            raidd_flags        = intel.get("raidd_flags", {
                "risks": [], "issues": [], "assumptions": [], "dependencies": [], "decisions": []
            })

            notes = str(raw_notes) if raw_notes else None

            # ── Prisma nested format — used ONLY for push ──
            key_points_prisma    = [{"content": str(k)} for k in raw_key_points    if k] if isinstance(raw_key_points,    list) else []
            action_points_prisma = [{"content": str(a)} for a in raw_action_points if a] if isinstance(raw_action_points, list) else []

            logger.info(
                f"DEBUG Meeting Payload → "
                f"aiMeetingSummary: {str(ai_meeting_summary)[:80] if ai_meeting_summary else None}, "
                f"agenda: {agenda}, notes: {notes}, "
                f"keyPoints: {key_points_prisma}, actionPoints: {action_points_prisma}"
            )

            push_meeting_result(
                meeting_id         = m_id,
                notes              = notes,
                agenda             = agenda,
                ai_meeting_summary = ai_meeting_summary,
                key_points         = {
                    "deleteMany": {},
                    "create": key_points_prisma
                },
                action_points      = {
                    "deleteMany": {},
                    "create": action_points_prisma
                },
                raidd_flags        = raidd_flags
            )

            # ── Return flat string lists, NOT Prisma format ──
            result = {
                "id":               m_id,
                "notes":            notes,
                "agenda":           agenda,
                "aiMeetingSummary": ai_meeting_summary,
                "keyPoints":        raw_key_points,
                "actionPoints":     raw_action_points,
                "raiddFlags":       raidd_flags
            }
            results.append(result)
            logger.info(f"Meeting [{m_id}] for '{p_name}' pushed successfully.")

            # Stop searching further projects if we found the specific meeting
            if meeting_id:
                break

        except Exception as e:
            logger.error(f"Meeting error '{p_name}' [{m_id}]: {e}", exc_info=True)

    logger.info(f"Meeting analysis done. {len(results)} meetings.")
    return results


# ── Document Analysis ─────────────────────────────────────
def analyze_all_documents(session_data: dict, document_id: str = None):
    projects = session_data.get("projects", [])
    logger.info(f"Document analysis...")
    results = []

    for project in projects:
        p_name    = project.get("name", "Unknown")
        documents = project.get("documents", [])

        if not documents:
            logger.info(f"No documents for '{p_name}'. Skipping.")
            continue

        # Filter to single document if id is provided
        if document_id:
            documents = [d for d in documents if d.get("id") == document_id]
            if not documents:
                logger.info(f"No document with id [{document_id}] in project '{p_name}'. Skipping.")
                continue

        for doc in documents:
            d_id = doc.get("id")
            try:
                intel      = run_document_summary(doc)
                ai_summary = intel.get("summary", "")

                key_points = [
                    {"content": str(k)} for k in intel.get("discussion_points", []) if k
                ]
                action_points = [
                    {"content": str(a)} for a in intel.get("action_points", []) if a
                ]

                push_document_result(
                    d_id,
                    ai_summary,
                    {"deleteMany": {}, "create": key_points},
                    {"deleteMany": {}, "create": action_points}
                )

                results.append({
                    "id":                d_id,
                    "aiDocumentSummary": ai_summary,
                    "keyPoints":         key_points,
                    "actionPoints":      action_points
                })
                logger.info(f"Document [{d_id}] pushed.")

            except Exception as e:
                logger.error(f"Document error [{d_id}]: {e}")

        # Stop searching further projects if we found the specific document
        if document_id and results:
            break

    logger.info(f"Document analysis done. {len(results)} documents.")
    return results