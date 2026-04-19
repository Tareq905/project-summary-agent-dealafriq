from fastapi import Header, HTTPException
from config.settings import settings

# This list allows your AI to accept BOTH the new secret and the old one
ALLOWED_KEYS = [
    getattr(settings, "BACKEND_SERVICE_SECRET", ""),
    "PROJECT_AI_BACKEND" # The legacy key other developers are likely using
]

async def verify_backend(x_backend_service: str = Header(None)):
    """
    This is what protects your AI API. 
    It will now accept the new secret OR the old legacy key.
    """
    if not x_backend_service:
        raise HTTPException(status_code=401, detail="Missing x-backend-service header")

    # Check if the key provided by the developer is in our allowed list
    if x_backend_service not in ALLOWED_KEYS:
        # This log will help you see EXACTLY what the other developer is sending
        print(f"DEBUG: Blocked unauthorized key: {x_backend_service}")
        raise HTTPException(status_code=401, detail="Invalid security token")

    return True