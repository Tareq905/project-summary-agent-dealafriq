from fastapi import Header, HTTPException
from config.settings import settings


async def verify_backend(x_backend_service: str = Header(None)):
    if not x_backend_service:
        raise HTTPException(status_code=401, detail="Missing x-backend-service header")

    allowed_keys = [settings.BACKEND_SERVICE_SECRET, "PROJECT_AI_BACKEND"]

    if x_backend_service not in allowed_keys:
        print(f"Unauthorized attempt with key: {x_backend_service}")
        raise HTTPException(status_code=401, detail="Invalid Security Token")

    return True