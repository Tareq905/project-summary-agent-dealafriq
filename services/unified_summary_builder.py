from agents.weekly_summary_agent import run_weekly_summary
from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score

def build_unified_summary(session_data):
    output = []
    # FIX: Get from "projects" key, as defined in session_data_builder.py
    projects = session_data.get("projects", [])
    session_logs = session_data.get("logs", []) 

    for project in projects:
        p_id = project.get("id")
        
        # 1. Match specific logs for this project
        project_activity_logs = next(
            (item for item in session_logs if item.get("projectId") == p_id), 
            {}
        )

        # 2. Run Project & Weekly Agents
        p_summary = run_project_summary(project)
        # Identify most recent meeting discussions via logs or transcripts
        w_summary = run_weekly_summary(project, project_activity_logs)
        
        # Extract Score safely from the health list
        health_list = project.get("health", [])
        raw_score = health_list[0].get("score") if health_list else 0
        p_score = float(raw_score) if raw_score is not None else 0.0

        # 3. Process Individual Documents
        docs_output = []
        for doc in project.get("documents", []):
            ai_doc_summary = run_document_summary(doc)
            docs_output.append({
                "documentId": doc.get("id"),
                "documentName": doc.get("fileName"), # Uses fileName from your API
                "uploadedDate": (doc.get("createdAt") or "").split("T")[0],
                "aiDocumentSummary": ai_doc_summary
            })

        # 4. Process Individual Meetings
        meetings_output = []
        latest_mtg_text = ""
        
        for mtg in project.get("meetings", []):
            ai_mtg_summary = run_meeting_summary(mtg)
            
            # Using projectSummary as the manual meeting summary from your API
            original_summary = mtg.get("projectSummary") or ""
            latest_mtg_text = original_summary 
            
            meetings_output.append({
                "meetingId": mtg.get("id"),
                "meetingDate": (mtg.get("meetingDate") or mtg.get("createdAt", "")).split("T")[0],
                "meetingSummary": original_summary,
                "aiMeetingSummary": ai_mtg_summary
            })

        # 5. Build final structured JSON
        output.append({
            "projectId": p_id,
            "projectSummary": p_summary,
            "weeklyMeetingSummary": w_summary,
            "projectScore": p_score,
            "documents": docs_output,
            "meetings": meetings_output,
            "latestMeetingSummary": latest_mtg_text
        })

    return output