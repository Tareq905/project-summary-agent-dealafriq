from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

def analyze_all_projects(all_sessions_data):
    """Generates high-level project intelligence with timeline math and milestones."""
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            # 1. Run Mathematical NSL to get velocity facts
            nsl_res = apply_nsl_logic(project)
            
            # 2. Run AI Agent with facts to get descriptive paragraphs
            intel = run_project_summary(project, nsl_res["facts"])
            
            # 3. Format Milestones with the "project progress" field
            milestones_output = []
            for m in project.get("milestones", []):
                milestones_output.append({
                    "id": m.get("id"),
                    "projectId": project.get("id"),
                    "title": m.get("title"),
                    "description": m.get("description"),
                    "project progress": nsl_res["progress_str"],
                    "milestoneDate": m.get("milestoneDate"),
                    "status": m.get("status"),
                    "createdAt": m.get("createdAt")
                })

            # 4. Construct the flat project object
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "flag": intel.get("flag", "Green"),
                "projectScore": float(run_health_score(project)),
                "summary": intel.get("summary"),
                "actionPoints": intel.get("action_points", []),
                "discussionPoints": intel.get("discussion_points", []),
                "notes": intel.get("notes", ""),
                "raiddFlags": intel.get("raidd_flags", {}),
                "milestones": milestones_output
            })
    return output

def analyze_all_meetings(all_sessions_data):
    """Generates granular intelligence for every meeting transcript."""
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            mtgs_list = []
            for mtg in project.get("meetings", []):
                # Call agent (returns summary, action_points, discussion_points, etc.)
                intel = run_meeting_summary(mtg)
                
                mtgs_list.append({
                    "meetingId": mtg.get("id"),
                    "meetingTitle": mtg.get("title"),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            
            # Group meetings under their project ID
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "meetings": mtgs_list
            })
    return output

def analyze_all_documents(all_sessions_data):
    """Generates detailed analysis for every uploaded project document."""
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            docs_list = []
            for doc in project.get("documents", []):
                # Call agent (returns summary, action_points, discussion_points, etc.)
                intel = run_document_summary(doc)
                
                docs_list.append({
                    "documentId": doc.get("id"),
                    "documentName": doc.get("fileName"),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            
            # Group documents under their project ID
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "documents": docs_list
            })
    return output