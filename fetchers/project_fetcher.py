import requests
from config.settings import settings

def fetch_session_projects(session: str):
    if session == "ONGOING":
        url = settings.ONGOING_PROJECT_API
    elif session == "COMPLETED":
        url = settings.COMPLETED_PROJECT_API
    elif session == "CANCELLED":
        url = settings.CANCELLED_PROJECT_API
    else:
        return []

    response = requests.get(url)
    if response.status_code == 200:
        # This returns the array of projects
        return response.json().get("data", []) 
    return []