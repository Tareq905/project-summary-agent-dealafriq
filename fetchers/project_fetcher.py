import requests
from config.settings import settings

def fetch_session_projects(session: str):
    """
    Fetches projects from the backend using the x-backend-service 
    header for authentication.
    """
    # 1. Determine the URL based on the session type
    if session == "ONGOING": 
        url = settings.ONGOING_PROJECT_API
    elif session == "COMPLETED": 
        url = settings.COMPLETED_PROJECT_API
    elif session == "CANCELLED": 
        url = settings.CANCELLED_PROJECT_API
    else: 
        print(f"DEBUG: Invalid session type: {session}")
        return []

    # 2. Define the headers required by your backend developer
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json"
    }

    try:
        print(f"DEBUG: Fetching {session} projects from {url}")
        
        # 3. Perform the GET request with the headers
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            json_res = response.json()
            
            # Support both raw list response and {data: []} wrapper
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or json_res.get("projects", [])
        
        print(f"DEBUG: Project API Error {response.status_code}: {response.text}")
        return []

    except Exception as e:
        print(f"DEBUG: Project Fetch Exception: {e}")
        return []