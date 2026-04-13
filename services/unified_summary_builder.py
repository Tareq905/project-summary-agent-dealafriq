from agents.weekly_summary_agent import run_weekly_summary
from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score

def build_unified_summary(session_data):
    output = []
    projects = session_data.get("projects", [])
    session_logs = session_data.get("logs", []) 

    for project in projects:
        try:
            p_id = project.get("id")
            project_activity_logs = next((item for item in session_logs if item.get("projectId") == p_id), {})
            transcripts = project_activity_logs.get("transcripts", [])

            # ... (Project summary & document logic remains the same)

            # 4. Meetings - UPDATED to use the new rich summary
            meetings_output = []
            for mtg in project.get("meetings", []):
                ai_mtg_intel = run_meeting_summary(mtg, transcripts)
                
                meetings_output.append({
                    "meetingId": mtg.get("id"),
                    "meetingDate": ai_mtg_intel.get("date"),
                    "formattedSummary": ai_mtg_intel.get("summary"),
                    "keyPoints": ai_mtg_intel.get("key_points", []),
                    "futurePlans": ai_mtg_intel.get("future_plans", []),
                    "tags": ai_mtg_intel.get("tags", []),
                    "flag": ai_mtg_intel.get("flag")
                })

            output.append({
                "projectId": p_id,
                "meetings": meetings_output,
                # ... other fields
            })
        except Exception as e:
            print(f"Error: {e}")
            continue

    return output