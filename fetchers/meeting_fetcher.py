import requests
from config.settings import settings


def fetch_all_meetings():
    url = settings.MEETING_GET_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    try:
        print(f"DEBUG: Fetching all meetings from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            outer_data = json_res.get("data", {})
            if isinstance(outer_data, list):
                return outer_data
            if isinstance(outer_data, dict):
                inner_data = outer_data.get("data", [])
                if isinstance(inner_data, list):
                    return inner_data
            return []
        print(f"❌ Meeting API error: {response.status_code} — {response.text}")
        return []
    except Exception as e:
        print(f"❌ Meeting fetch exception: {e}")
        return []