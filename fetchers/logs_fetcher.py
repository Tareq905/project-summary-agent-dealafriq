import requests
from config.settings import settings

def fetch_session_logs(session: str):
    if session == "ONGOING": url = settings.ONGOING_LOG_API
    elif session == "COMPLETED": url = settings.COMPLETED_LOG_API
    elif session == "CANCELLED": url = settings.CANCELLED_LOG_API
    else: return []

    try:
        print(f"DEBUG: Fetching logs from {url}")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            # Handle different backend wrappers
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or json_res.get("logs", [])
        return []
    except Exception as e:
        print(f"DEBUG: Log Fetch Error: {e}")
        return []