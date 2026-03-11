import requests
from config.settings import settings

def fetch_session_projects(session: str):
    # Map to the .env keys
    if session == "ONGOING": url = settings.ONGOING_PROJECT_API
    elif session == "COMPLETED": url = settings.COMPLETED_PROJECT_API
    elif session == "CANCELLED": url = settings.CANCELLED_PROJECT_API
    else: return []

    try:
        print(f"DEBUG: Fetching projects from {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            json_res = response.json()
            # Handle both wrapped {"data": [...]} and raw list [...]
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or json_res.get("projects", [])
        
        print(f"DEBUG: Project API returned status {response.status_code}")
        return []
    except Exception as e:
        print(f"DEBUG: Project Fetch Error: {e}")
        return []