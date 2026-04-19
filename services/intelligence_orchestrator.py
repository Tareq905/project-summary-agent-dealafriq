from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

def analyze_all_projects(all_sessions_data):
    """
    Analyzes project status. 
    Maintains a FLAT structure and ENSURES Completed/Cancelled appear 
    even when the backend returns 0 projects.
    """
    output = []
    
    # This loops through ONGOING, COMPLETED, CANCELLED
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])

        # --- THE FIX: Add this block to handle empty sessions ---
        if not projects:
            output.append({
                "projectId": None,
                "projectName": "No projects in this session",
                "session": session_name,
                "flag": "Green",
                "projectScore": 0.0,
                "summary": "No data available.",
                "actionPoints": [],
                "discussionPoints": [],
                "notes": "No projects found for this status.",
                "raiddFlags": {
                    "risks": [],
                    "assumptions": [],
                    "issues": [],
                    "dependencies": [],
                    "decisions": []
                },
                "milestones": []
            })
            continue # Move to the next session
        # -------------------------------------------------------

        # If projects EXIST, run the normal AI analysis
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
                    "projectScore": float(calculated_score),
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
    """
    Generates meeting intelligence.
    Maintains the FLAT structure but forces empty sessions to appear.
    """
    output = []
    
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        logs = data.get("logs", [])

        # --- NEW LOGIC: If a session is empty, add a placeholder ---
        if not projects:
            output.append({
                "projectId": None,
                "projectName": "No projects in this session",
                "session": session_name,
                "meetings": []
            })
            continue 
        # -----------------------------------------------------------

        for project in projects:
            p_id = project.get("id")
            root_mtgs = project.get("meetings", [])
            project_log = next((item for item in logs if item.get("id") == p_id), {})
            transcripts = project_log.get("transcripts", [])
            
            mtgs_list = []
            for mtg in root_mtgs:
                if not mtg or 'id' not in mtg: continue
                
                intel = run_meeting_summary(mtg, transcripts)
                
                mtgs_list.append({
                    "meetingId": mtg.get("id"),
                    "meetingTitle": mtg.get("title") or "Project Meeting",
                    "summary": intel.get("summary"),
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
                "projectName": project.get("name"),
                "session": session_name,
                "meetings": mtgs_list
            })
            
    return output

def analyze_all_documents(all_sessions_data):
    """
    Generates detailed analysis for every uploaded document.
    Maintains a FLAT structure and forces placeholders for empty sessions.
    """
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        logs = data.get("logs", [])

        # --- THE FIX: If no projects exist, add a placeholder for the session ---
        if not projects:
            output.append({
                "projectId": None,
                "session": session_name,
                "documents": []
            })
            continue 
        # -----------------------------------------------------------------------

        for project in projects:
            p_id = project.get("id")
            
            # 1. Gather documents from project root
            root_docs = project.get("documents", [])
            
            # 2. Gather documents from activity logs
            project_log = next((item for item in logs if item.get("id") == p_id), {})
            activities = project_log.get("activities", [])
            log_docs = [a.get("crudData") for a in activities if a.get("type") == "document" and a.get("crudData")]
            
            # 3. Merge and deduplicate documents
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
            
            # 4. Add the project documents to the flat output list
            output.append({
                "projectId": p_id,
                "session": session_name,
                "documents": docs_list
            })
            
    return output