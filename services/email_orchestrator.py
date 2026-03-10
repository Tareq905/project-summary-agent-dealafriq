# services/email_orchestrator.py
from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis

def analyze_all_emails():
    # 1. Fetch data from APIs
    emails = fetch_all_emails()
    projects = fetch_all_projects_for_context()

    # 2. Process each email
    output =[]
    for email in emails:
        # Pass the email and the projects list to the AI
        analysis_result = run_email_analysis(email, projects)
        
        if analysis_result:
            # Attach the original additional_info/metadata as requested
            analysis_result["additional_info"] = {
                "gmailMessageId": email.get("gmailMessageId"),
                "receivedAt": email.get("receivedAt"),
                "category": email.get("category")
            }
            output.append(analysis_result)

    return output