import logging
from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis
from services.pusher import push_email_result

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_all_emails(email_id: str = None):
    logger.info("🚀 Starting Global Email Analysis Process...")

    emails   = fetch_all_emails()
    projects = fetch_all_projects_for_context()

    if email_id:
        emails = [e for e in emails if e.get("id") == email_id]
        if not emails:
            logger.warning(f"⚠️ No email found with id: {email_id}")
            return []

    total_emails = len(emails)
    logger.info(f"📥 Fetched {total_emails} emails. Found {len(projects)} projects for context.")

    if total_emails == 0:
        logger.warning("⚠️ No emails found to analyze.")
        return []

    output = []

    for index, email in enumerate(emails, start=1):
        e_id = email.get("id", "Unknown_ID")
        logger.info(f"🔍 [{index}/{total_emails}] Analyzing email: {e_id}")

        try:
            analysis_result = run_email_analysis(email, projects)

            if analysis_result:
                raidd = analysis_result.get("raiddAnalysis", {})

                # ── Build raidd_data with all 7 categories ──
                raidd_data = {
                    "risks":        [{"data": d} for d in raidd.get("risks", [])        if d],
                    "issues":       [{"data": d} for d in raidd.get("issues", [])       if d],
                    "assumptions":  [{"data": d} for d in raidd.get("assumptions", [])  if d],
                    "dependencies": [{"data": d} for d in raidd.get("dependencies", []) if d],
                    "tasks":        [{"data": d} for d in raidd.get("tasks", [])        if d],
                    "actions":      [{"data": d} for d in raidd.get("actions", [])      if d],
                    "nextSteps":    [{"data": d} for d in raidd.get("nextSteps", [])    if d],
                }

                push_email_result(
                    email_id        = e_id,
                    summary         = analysis_result.get("summary", ""),
                    tasks           = [],
                    raidd_category  = analysis_result.get("category", []),
                    raidd_data      = raidd_data,
                    generated_reply = analysis_result.get("generatedReply", "")
                )

                output.append({
                    "flag":      analysis_result.get("flag", "Green"),
                    "emailId":   analysis_result.get("emailId", e_id),
                    "summary":   analysis_result.get("summary", ""),
                    "category":  analysis_result.get("category", []),
                    "sentiment": analysis_result.get("sentiment", "neutral"),
                    "raiddAnalysis": raidd,
                    "additional_info": {
                        "category":       email.get("category"),
                        "receivedAt":     email.get("receivedAt"),
                        "gmailMessageId": email.get("gmailMessageId")
                    },
                    "generatedReply": analysis_result.get("generatedReply"),
                    "vendor": None,
                    "type":   "gmail"
                })
                logger.info(f"✅ Successfully analyzed and pushed email: {e_id}")
            else:
                logger.error(f"❌ AI failed to return a valid result for email: {e_id}")

        except Exception as e:
            logger.error(f"💥 Critical error analyzing email {e_id}: {str(e)}")
            continue

    logger.info(f"✅ Email Analysis Complete. Successfully processed {len(output)}/{total_emails} emails.")
    return output