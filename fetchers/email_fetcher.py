import requests
from config.settings import settings

def fetch_all_emails():
    url = settings.EMAIL_GET_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    try:
        print(f"DEBUG: Fetching all emails from {url}")
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            if isinstance(json_res, list):
                return json_res
            data = json_res.get("data", [])
            if isinstance(data, list):
                return data
            return []
        print(f"❌ Email API error: {response.status_code} — {response.text}")
        return []
    except Exception as e:
        print(f"❌ Email fetch exception: {e}")
        return []


def fetch_all_projects_for_context():
    url = settings.PROJECT_GET_API
    headers = {
        "x-backend-service": settings.BACKEND_SERVICE_SECRET,
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            if isinstance(json_res, list):
                return json_res
            return json_res.get("data", []) or json_res.get("projects", []) or []
        print(f"❌ Project context fetch error: {response.status_code}")
        return []
    except Exception as e:
        print(f"❌ Project context fetch exception: {e}")
        return []