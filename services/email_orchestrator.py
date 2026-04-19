from fetchers.email_fetcher import fetch_all_emails, fetch_all_projects_for_context
from agents.email_summary_agent import run_email_analysis

def analyze_all_emails():
    emails = fetch_all_emails()
    projects = fetch_all_projects_for_context()

    output = []
    for email in emails:
        analysis_result = run_email_analysis(email, projects)
        
        if analysis_result:
            # EXACT STRUCTURE MATCHING YOUR REQUIREMENT
            output.append({
                "flag": analysis_result.get("flag", "Green"),
                "emailId": analysis_result.get("emailId"),
                "summary": analysis_result.get("summary"),
                "category": analysis_result.get("category", ["Informational"]),
                "sentiment": analysis_result.get("sentiment"),
                "raiddAnalysis": analysis_result.get("raiddAnalysis"),
                "additional_info": {
                    "category": email.get("category"), 
                    "receivedAt": email.get("receivedAt"),
                    "gmailMessageId": email.get("gmailMessageId")
                },
                "generatedReply": None,
                "vendor": None,
                "type": "gmail"
            })

    return output