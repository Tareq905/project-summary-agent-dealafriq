from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

def analyze_all_projects(all_sessions_data):
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        for project in projects:
            try:
                # 1. Run Mathematical NSL
                nsl_res = apply_nsl_logic(project)
                
                # 2. Run AI Agent
                intel = run_project_summary(project, nsl_res["facts"])
                
                # 3. Calculate Score using NSL Math
                calculated_score = run_health_score(project, nsl_res)

                output.append({
                    "projectId": project.get("id"),
                    "projectName": project.get("name"),
                    "session": session_name,
                    "flag": intel.get("flag", "Unknown"),
                    "projectScore": float(calculated_score), # NOW FIXED
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {}),
                    "milestones": [{
                        "id": m.get("id"),
                        "title": m.get("title"),
                        "project progress": nsl_res["progress_str"],
                        "milestoneDate": m.get("milestoneDate"),
                        "status": m.get("status")
                    } for m in project.get("milestones", [])]
                })
            except Exception as e:
                print(f"ERROR project {project.get('id')}: {e}")
                continue
    return output

def analyze_all_meetings(all_sessions_data):
    """Generates intelligence while strictly maintaining the original JSON architecture."""
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        logs = data.get("logs", [])

        for project in projects:
            p_id = project.get("id")
            
            root_mtgs = project.get("meetings", [])
            project_log = next((item for item in logs if item.get("id") == p_id), {})
            transcripts = project_log.get("transcripts", [])
            
            # Map meetings
            mtgs_list = []
            for mtg in root_mtgs:
                if not mtg or 'id' not in mtg: continue
                
                # Run Agent
                intel = run_meeting_summary(mtg, transcripts)
                
                # STRICT ARCHITECTURE MAPPING
                mtgs_list.append({
                    "meetingId": mtg.get("id"),
                    "meetingTitle": mtg.get("title") or "Project Meeting",
                    "summary": intel.get("summary"), # Contains the 🔹 formatted text
                    "agenda": {
                        "meetingTopics": intel.get("agenda", {}).get("meetingTopics", []),
                        "coreDiscussionPoints": intel.get("agenda", {}).get("coreDiscussionPoints", [])
                    },
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            
            output.append({
                "projectId": p_id,
                "session": session_name,
                "meetings": mtgs_list
            })
    return output

def analyze_all_documents(all_sessions_data):
    """Generates detailed analysis for every uploaded document.
    Structure remains constant as requested.
    """
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        logs = data.get("logs", [])

        for project in projects:
            p_id = project.get("id")
            
            root_docs = project.get("documents", [])
            project_log = next((item for item in logs if item.get("id") == p_id), {})
            activities = project_log.get("activities", [])
            
            log_docs = [a.get("crudData") for a in activities if a.get("type") == "document" and a.get("crudData")]
            unique_docs = {d['id']: d for d in (root_docs + log_docs) if d and 'id' in d}.values()

            docs_list = []
            for doc in unique_docs:
                intel = run_document_summary(doc)
                docs_list.append({
                    "documentId": doc.get("id"),
                    "documentName": doc.get("fileName") or doc.get("title"),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            
            output.append({
                "projectId": p_id,
                "session": session_name,
                "documents": docs_list
            })
    return output