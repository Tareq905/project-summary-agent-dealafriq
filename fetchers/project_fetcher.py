import requests
from config.settings import settings

def fetch_session_projects(session: str):
    """
    Fetches projects from the backend. 
    Uses BACKEND_SERVICE_SECRET for the security handshake.
    """
    # 1. Determine the URL based on the session type
    if session == "ONGOING": 
        url = settings.ONGOING_PROJECT_API
    elif session == "COMPLETED": 
        url = settings.COMPLETED_PROJECT_API
    elif session == "CANCELLED": 
        url = settings.CANCELLED_PROJECT_API
    else: 
        print(f"DEBUG: Invalid session type requested: {session}")
        return []

    # 2. Identify the Security Token
    # We use the new Secret, but provide a hardcoded fallback 
    # just in case the .env is not yet updated on the server.
    auth_token = getattr(settings, "BACKEND_SERVICE_SECRET", "PROJECT_AI_BACKEND")

    # 3. Define the headers for the Outgoing Request (AI -> Backend)
    headers = {
        "x-backend-service": auth_token,
        "Content-Type": "application/json"
    }

    try:
        print(f"DEBUG: AI Service calling Backend API: {url}")
        
        # 4. Perform the GET request
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            json_res = response.json()
            
            # Handle list-style or object-style responses
            if isinstance(json_res, list):
                return json_res
            
            # Extract data from nested keys used by common backend frameworks
            return (json_res.get("data", []) or 
                    json_res.get("projects", []) or 
                    json_res.get("payload", []))
        
        # If the backend returns an error (like 401), we log it here
        print(f"CRITICAL: Backend rejected AI Request. Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        return []

    except Exception as e:
        print(f"EXCEPTION during project fetch: {str(e)}")
        return []