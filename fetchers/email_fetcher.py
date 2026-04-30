import requests
from config.settings import settings

def fetch_all_emails():
    """
    Fetches all emails from the backend.
    Includes robust error handling and debug printing.
    """
    url = settings.ALL_EMAILS_API
    headers = {"x-backend-service": settings.BACKEND_SERVICE_SECRET}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            
            # --- DEBUG PRINT (Essential for seeing what the backend actually sends) ---
            print(f"DEBUG: Raw Backend Email Response: {json_res}")
            # -------------------------------------------------------------------------

            # If the response is already a list, return it
            if isinstance(json_res, list):
                return json_res
            
            # If the response is a dictionary, try to find the list in common keys
            return (json_res.get("data", []) or 
                    json_res.get("emails", []) or 
                    json_res.get("payload", []))
        else:
            print(f"❌ Error fetching emails: Status {response.status_code}")
            print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        
    return []

def fetch_all_projects_for_context():
    """
    Fetches all projects from the backend to provide context 
    for the Email Agent (e.g., to map an email to a project).
    """
    url = settings.ALL_PROJECTS_PUBLIC_API
    headers = {"x-backend-service": settings.BACKEND_SERVICE_SECRET}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            json_res = response.json()
            
            # Debugging project fetch
            print(f"DEBUG: Raw Backend Project Response: {json_res}")

            if isinstance(json_res, list):
                return json_res
            
            # Try to find the list in common keys used by backend frameworks
            return (json_res.get("data", []) or 
                    json_res.get("projects", []) or 
                    json_res.get("payload", []))
        else:
            print(f"❌ Error fetching projects: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")
        
    return []