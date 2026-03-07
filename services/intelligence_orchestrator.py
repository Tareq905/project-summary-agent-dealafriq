from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score

def analyze_all_projects(all_sessions_data):
    # Returns a flat list [] instead of a dictionary grouped by session
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            intel = run_project_summary(project)
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "flag": intel.get("flag", "Green"),
                "projectScore": float(run_health_score(project)),
                "summary": intel.get("summary"),
                "actionPoints": intel.get("action_points", []),
                "discussionPoints": intel.get("discussion_points", []),
                "notes": intel.get("notes", ""),
                "raiddFlags": intel.get("raidd_flags", {})
            })
    return output

def analyze_all_meetings(all_sessions_data):
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            mtgs = []
            for mtg in project.get("meetings", []):
                intel = run_meeting_summary(mtg)
                mtgs.append({
                    "meetingId": mtg.get("id"),
                    "meetingTitle": mtg.get("title"),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "meetings": mtgs
            })
    return output

def analyze_all_documents(all_sessions_data):
    output = []
    for session_name, data in all_sessions_data.items():
        for project in data.get("projects", []):
            docs = []
            for doc in project.get("documents", []):
                intel = run_document_summary(doc)
                docs.append({
                    "documentId": doc.get("id"),
                    "documentName": doc.get("fileName"),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {})
                })
            output.append({
                "projectId": project.get("id"),
                "session": session_name,
                "documents": docs
            })
    return output