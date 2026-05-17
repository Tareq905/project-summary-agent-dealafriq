import requests
from config.settings import settings


def fetch_all_clients():
    url = settings.CLIENT_GET_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    try:
        print(f"DEBUG: Fetching all clients from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            data = json_res.get("data", [])
            if isinstance(data, list):
                return data
            return []
        print(f"❌ Client API error: {response.status_code} — {response.text}")
        return []
    except Exception as e:
        print(f"❌ Client fetch exception: {e}")
        return []