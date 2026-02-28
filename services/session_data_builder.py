from fetchers.logs_fetcher import fetch_session_logs
from fetchers.project_fetcher import fetch_session_projects

def build_session_data(session: str):
    projects = fetch_session_projects(session)
    logs = fetch_session_logs(session)
    return {
        "projects": projects,
        "logs": logs
    }