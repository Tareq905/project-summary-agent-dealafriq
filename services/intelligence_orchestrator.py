from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

def analyze_all_projects(all_sessions_data):
    """
    Analyzes project status. Returns a simple list of strings for each RAIDD category.
    Includes placeholders for empty sessions.
    """
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        
        # 1. Handle Empty Sessions for Frontend Consistency
        if not projects:
            output.append({
                "projectId": None,
                "projectName": "No projects found",
                "session": session_name,
                "flag": "Green",
                "projectScore": 0.0,
                "summary": "No data available.",
                "actionPoints": [],
                "discussionPoints": [],
                "notes": "No active projects in this session.",
                "raiddFlags": {
                    "risks": [], "assumptions": [], "issues": [], "dependencies": [], "decisions": []
                },
                "milestones": []
            })
            continue

        for project in projects:
            try:
                # 2. Logic & AI Agents
                nsl_res = apply_nsl_logic(project)
                intel = run_project_summary(project, nsl_res["facts"])
                calculated_score = run_health_score(project, nsl_res)

                # 3. Standardize RAIDD to Lists of Strings
                raw_raidd = intel.get("raidd_flags", {})
                
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
                    "raiddFlags": {
                        "risks": raw_raidd.get("risks", []),
                        "assumptions": raw_raidd.get("assumptions", []),
                        "issues": raw_raidd.get("issues", []),
                        "dependencies": raw_raidd.get("dependencies", []),
                        "decisions": raw_raidd.get("decisions", [])
                    },
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
    Ensures RAIDD items are simple lists of descriptive strings.
    """
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        logs = data.get("logs", [])

        if not projects:
            output.append({
                "projectId": None,
                "projectName": "No projects found",
                "session": session_name,
                "documents": []
            })
            continue 

        for project in projects:
            p_id = project.get("id")
            
            # Harvesting docs from root and logs
            root_docs = project.get("documents", [])
            project_log = next((item for item in logs if item.get("id") == p_id), {})
            activities = project_log.get("activities", [])
            log_docs = [a.get("crudData") for a in activities if a.get("type") == "document" and a.get("crudData")]
            
            unique_docs = {d['id']: d for d in (root_docs + log_docs) if d and 'id' in d}.values()

            docs_list = []
            for doc in unique_docs:
                try:
                    intel = run_document_summary(doc)
                    raw_raidd = intel.get("raidd_flags", {})

                    docs_list.append({
                        "documentId": doc.get("id"),
                        "documentName": doc.get("fileName") or doc.get("title"),
                        "summary": intel.get("summary"),
                        "actionPoints": intel.get("action_points", []),
                        "discussionPoints": intel.get("discussion_points", []),
                        "notes": intel.get("notes", ""),
                        "raiddFlags": {
                            "risks": raw_raidd.get("risks", []),
                            "assumptions": raw_raidd.get("assumptions", []),
                            "issues": raw_raidd.get("issues", []),
                            "dependencies": raw_raidd.get("dependencies", []),
                            "decisions": raw_raidd.get("decisions", [])
                        }
                    })
                except Exception as e:
                    print(f"Error analyzing document {doc.get('id')}: {e}")
                    continue
            
            output.append({
                "projectId": p_id,
                "projectName": project.get("name"),
                "session": session_name,
                "documents": docs_list
            })
    return output