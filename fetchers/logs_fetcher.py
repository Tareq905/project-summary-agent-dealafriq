import requests
from config.settings import settings

def fetch_session_logs(session: str):
    # Determine the correct URL from settings
    if session == "ONGOING": 
        url = settings.ONGOING_LOG_API
    elif session == "COMPLETED": 
        url = settings.COMPLETED_LOG_API
    elif session == "CANCELLED": 
        url = settings.CANCELLED_LOG_API
    else: 
        return []

    # MUST include the header provided by your developer
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json"
    }

    try:
        print(f"DEBUG: AI Fetching {session} logs from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            json_res = response.json()
            # Handle both list and object wrappers
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or json_res.get("logs", [])
            
        print(f"DEBUG: Log API Error {response.status_code} for session {session}")
        return []
    except Exception as e:
        print(f"DEBUG: Log Fetch Exception ({session}): {e}")
        return []