import requests
from config.settings import settings

def fetch_all_emails():
    url = settings.ALL_EMAILS_API
    headers = {"x-backend-service": settings.BACKEND_SERVICE_SECRET}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching emails: {e}")
    return []

def fetch_all_projects_for_context():
    url = settings.ALL_PROJECTS_PUBLIC_API
    headers = {"x-backend-service": settings.BACKEND_SERVICE_SECRET}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching projects context: {e}")
    return []