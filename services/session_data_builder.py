from fetchers.logs_fetcher import fetch_session_logs
from fetchers.project_fetcher import fetch_session_projects

def build_all_sessions_data():
    sessions = ["ONGOING", "COMPLETED", "CANCELLED"]
    all_data = {}

    for s in sessions:
        projects = fetch_session_projects(s)
        logs = fetch_session_logs(s)
        
        # DEBUG: Check if data is actually arriving
        print(f"--- SESSION BUILDER DEBUG ---")
        print(f"Session: {s}")
        print(f"Projects Found: {len(projects)}")
        print(f"Logs Found: {len(logs)}")
        print(f"-----------------------------")

        all_data[s] = {
            "projects": projects,
            "logs": logs
        }
    
    return all_data