from agents.weekly_summary_agent import run_weekly_summary
from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score

def build_unified_summary(session_data):
    output = []
    
    # CRITICAL: This must match the key used in build_session_data
    projects = session_data.get("projects", [])
    session_logs = session_data.get("logs", []) 

    # Debug Print: See if projects are actually reaching this function
    print(f"DEBUG: Processing {len(projects)} projects for summary...")

    for project in projects:
        try:
            p_id = project.get("id")
            
            # 1. Match specific logs
            project_activity_logs = next(
                (item for item in session_logs if item.get("projectId") == p_id), 
                {}
            )

            # 2. Run Agents
            p_summary = run_project_summary(project)
            w_summary = run_weekly_summary(project, project_activity_logs)
            
            health_list = project.get("health", [])
            raw_score = health_list[0].get("score") if health_list else 0
            p_score = float(raw_score) if raw_score is not None else 0.0

            # 3. Documents
            docs_output = []
            for doc in project.get("documents", []):
                ai_doc_summary = run_document_summary(doc)
                docs_output.append({
                    "documentId": doc.get("id"),
                    "documentName": doc.get("fileName") or "Untitled",
                    "uploadedDate": (doc.get("createdAt") or "").split("T")[0],
                    "aiDocumentSummary": ai_doc_summary
                })

            # 4. Meetings
            meetings_output = []
            latest_mtg_text = ""
            for mtg in project.get("meetings", []):
                ai_mtg_summary = run_meeting_summary(mtg)
                original_summary = mtg.get("projectSummary") or ""
                latest_mtg_text = original_summary 
                
                meetings_output.append({
                    "meetingId": mtg.get("id"),
                    "meetingDate": (mtg.get("meetingDate") or mtg.get("createdAt", "")).split("T")[0],
                    "meetingSummary": original_summary,
                    "aiMeetingSummary": ai_mtg_summary
                })

            # 5. Append to Output
            output.append({
                "projectId": p_id,
                "projectSummary": p_summary,
                "weeklyMeetingSummary": w_summary,
                "projectScore": p_score,
                "documents": docs_output,
                "meetings": meetings_output,
                "latestMeetingSummary": latest_mtg_text
            })
        except Exception as e:
            print(f"ERROR processing project {project.get('id')}: {e}")
            continue

    return output