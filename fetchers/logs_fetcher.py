import requests
from config.settings import settings

def fetch_session_logs(session: str):

    if session == "ONGOING":
        url = settings.ONGOING_LOG_API
    elif session == "COMPLETED":
        url = settings.COMPLETED_LOG_API
    elif session == "CANCELLED":
        url = settings.CANCELLED_LOG_API
    else:
        return []

    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception:
        return []