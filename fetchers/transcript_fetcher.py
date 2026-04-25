import requests
from config.settings import settings

def fetch_meeting_transcripts():
    # Strictly using the URL from .env
    url = settings.MEETING_TRANSCRIPT_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Accept": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            json_res = response.json()
            data = json_res.get("data")

            # Normalization: If data is a single dict, wrap in a list
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            return []
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"Fetch failed: {e}")
        return []