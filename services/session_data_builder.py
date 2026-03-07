from fetchers.logs_fetcher import fetch_session_logs
from fetchers.project_fetcher import fetch_session_projects

def build_all_sessions_data():
    """
    Fetches projects and logs for all sessions and groups them.
    """
    sessions = ["ONGOING", "COMPLETED", "CANCELLED"]
    all_data = {}

    for s in sessions:
        projects = fetch_session_projects(s)
        logs = fetch_session_logs(s)
        all_data[s] = {
            "projects": projects,
            "logs": logs
        }
    
    return all_data