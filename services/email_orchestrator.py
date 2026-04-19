from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis

def analyze_all_emails():
    # 1. Fetch data from backend
    emails = fetch_all_emails()
    projects = fetch_all_projects_for_context()

    print(f"DEBUG: Processing {len(emails)} emails")

    output = []
    for email in emails:
        # 2. Run AI Analysis
        analysis_result = run_email_analysis(email, projects)
        
        if analysis_result:
            # 3. Build the structure exactly as you requested
            output.append({
                "emailId": analysis_result.get("emailId"),
                "summary": analysis_result.get("summary"),
                "category": analysis_result.get("category", ["Informational"]),
                "flag": analysis_result.get("flag", "Green"),
                "raiddAnalysis": analysis_result.get("raiddAnalysis"),
                "sentiment": analysis_result.get("sentiment"),
                "additional_info": {
                    "gmailMessageId": email.get("gmailMessageId"),
                    "receivedAt": email.get("receivedAt"),
                    "category": email.get("category") # Raw source: personal, work, etc.
                }
            })

    return output