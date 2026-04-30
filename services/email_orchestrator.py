import logging
from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_all_emails():
    """
    Orchestrates the analysis of all fetched emails using the Supervised AI Agent.
    """
    logger.info("🚀 Starting Global Email Analysis Process...")

    emails = fetch_all_emails()
    projects = fetch_all_projects_for_context()
    
    total_emails = len(emails)
    logger.info(f"📥 Fetched {total_emails} emails. Found {len(projects)} projects for context.")

    if total_emails == 0:
        logger.warning("⚠️ No emails found to analyze.")
        return []

    output = []
    
    for index, email in enumerate(emails, start=1):
        email_id = email.get('id', 'Unknown_ID')
        logger.info(f"🔍 [{index}/{total_emails}] Analyzing email: {email_id}")

        try:
            analysis_result = run_email_analysis(email, projects)
            
            if analysis_result:
                output.append({
                    "flag": analysis_result.get("flag", "Green"),
                    "emailId": analysis_result.get("emailId", email_id),
                    "summary": analysis_result.get("summary", "No summary generated."),
                    "category": analysis_result.get("category", ["Informational"]),
                    "sentiment": analysis_result.get("sentiment", "neutral"),
                    "raiddAnalysis": analysis_result.get("raiddAnalysis", {
                        "risks": [], "issues": [], "decisions": [], "assumptions": [], "dependencies": []
                    }),
                    "additional_info": {
                        "category": email.get("category"), 
                        "receivedAt": email.get("receivedAt"),
                        "gmailMessageId": email.get("gmailMessageId")
                    },
                    "generatedReply": None,
                    "vendor": None,
                    "type": "gmail"
                })
                logger.info(f"✅ Successfully analyzed email: {email_id}")
            else:
                logger.error(f"❌ AI failed to return a valid result for email: {email_id}")

        except Exception as e:
            logger.error(f"💥 Critical error analyzing email {email_id}: {str(e)}")
            continue

    logger.info(f"🏁 Email Analysis Complete. Successfully processed {len(output)}/{total_emails} emails.")
    return output