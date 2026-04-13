import requests
from config.settings import settings

def fetch_all_vendor_data():
    url = settings.VENDOR_MANAGEMENT_API
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching vendors from {url}: {e}")
    return []

def fetch_pm_context():
    url = settings.PROJECT_MANAGERS_API
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching PMs from {url}: {e}")
    return []