import logging
from services.session_data_builder import build_session_data
from agents.weekly_summary_agent import run_weekly_summary
from services.pusher import push_weekly_summary

logger = logging.getLogger(__name__)


def analyze_and_push_weekly_summaries():
    """
    Standalone Weekly Summary Orchestrator.
    Fetches all projects, generates weekly AI summary for each,
    and automatically pushes to backend.
    """
    logger.info("🗓️ [WEEKLY] Starting Weekly Summary Generation...")

    try:
        session_data = build_session_data()
        projects = session_data.get("projects", [])
    except Exception as e:
        logger.error(f"❌ [WEEKLY] Failed to fetch session data: {e}")
        return []

    total = len(projects)
    logger.info(f"📦 [WEEKLY] Found {total} projects to process.")

    if not projects:
        logger.warning("⚠️ [WEEKLY] No projects found.")
        return []

    results = []

    for index, project in enumerate(projects, start=1):
        p_id   = project.get("id")
        p_name = project.get("name", "Unknown")
        logger.info(f"🔍 [WEEKLY] [{index}/{total}] Generating weekly summary for '{p_name}'...")

        try:
            # Generate weekly summary using the agent
            weekly_raw  = run_weekly_summary(project, [])
            weekly_text = (
                weekly_raw.get("weekly_summary") or
                weekly_raw.get("summary", "")
                if isinstance(weekly_raw, dict)
                else str(weekly_raw)
            )

            if not weekly_text:
                logger.warning(f"⚠️ [WEEKLY] Empty summary for '{p_name}'. Skipping push.")
                continue

            # Auto push to backend
            push_result = push_weekly_summary(p_id, weekly_text)

            results.append({
                "weeklyAiSummary": weekly_text
            })

            if push_result:
                logger.info(f"✅ [WEEKLY] '{p_name}' weekly summary pushed successfully.")
            else:
                logger.error(f"❌ [WEEKLY] '{p_name}' push failed.")

        except Exception as e:
            logger.error(f"💥 [WEEKLY] Error processing '{p_name}': {e}")
            continue

    logger.info(f"🏁 [WEEKLY] Done. {len(results)}/{total} weekly summaries pushed.")
    return results