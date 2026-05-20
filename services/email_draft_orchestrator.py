import logging
from fetchers.email_fetcher import fetch_all_emails
from agents.email_draft_agent import run_email_draft

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_email_draft(email_id: str) -> dict:
    """
    Email Draft Orchestrator.
    Fetches email by ID, generates a fresh draft, and returns it.
    No push — backend fetches directly from this endpoint.
    Safe to call repeatedly for regeneration.
    """
    logger.info(f"📧 [EMAIL_DRAFT] Starting draft generation for email ID: {email_id}")

    # ── 1. Fetch and find target email ────────────────────────
    all_emails = fetch_all_emails()

    if not all_emails:
        logger.warning("⚠️ [EMAIL_DRAFT] No emails returned from fetcher.")
        return _error_response(email_id, "No emails available.")

    target_email = next(
        (e for e in all_emails if e.get("id") == email_id),
        None
    )

    if not target_email:
        logger.warning(f"⚠️ [EMAIL_DRAFT] Email not found with ID: {email_id}")
        return _error_response(email_id, f"Email with ID '{email_id}' not found.")

    logger.info(
        f"✅ [EMAIL_DRAFT] Email found — "
        f"Subject: '{target_email.get('subject', 'N/A')[:60]}'"
    )

    # ── 2. Run the draft agent ────────────────────────────────
    logger.info(f"🤖 [EMAIL_DRAFT] Running draft agent...")
    draft = run_email_draft(target_email)

    if not draft:
        logger.error(f"❌ [EMAIL_DRAFT] Agent returned None for email ID: {email_id}")
        return _error_response(email_id, "AI draft generation failed.")

    logger.info(f"✅ [EMAIL_DRAFT] Draft generated successfully for email ID: {email_id}")

    # ── 3. Return response — no push ─────────────────────────
    return {
        "success": True,
        "emailId": email_id,
        "draft": {
            "subject":  draft.get("subject", ""),
            "greeting": draft.get("greeting", ""),
            "body":     draft.get("body", "")
        }
    }


def _error_response(email_id: str, message: str) -> dict:
    return {
        "success": False,
        "emailId": email_id,
        "error":   message,
        "draft":   None
    }