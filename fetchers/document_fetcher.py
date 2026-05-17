import requests
from config.settings import settings


def fetch_all_documents():
    url = settings.DOCUMENT_GET_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    try:
        print(f"DEBUG: Fetching all documents from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            if isinstance(json_res, list):
                return json_res
            data = json_res.get("data", [])
            if isinstance(data, list):
                return data
            return []
        print(f"❌ Document API error: {response.status_code} — {response.text}")
        return []
    except Exception as e:
        print(f"❌ Document fetch exception: {e}")
        return []