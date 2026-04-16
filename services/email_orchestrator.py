# services/email_orchestrator.py
from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis

def analyze_all_emails():
    emails = fetch_all_emails()
    projects = fetch_all_projects_for_context()

    output = []
    for email in emails:
        analysis_result = run_email_analysis(email, projects)
        
        if analysis_result:
            # The AI result already contains 'category' now.
            # We attach additional_info as usual.
            analysis_result["additional_info"] = {
                "gmailMessageId": email.get("gmailMessageId"),
                "receivedAt": email.get("receivedAt"),
                "category": email.get("category") # Raw source category (e.g. 'personal')
            }
            output.append(analysis_result)

    return output