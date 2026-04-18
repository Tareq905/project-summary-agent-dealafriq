from fastapi import Header, HTTPException
from config.settings import settings

async def verify_backend(x_backend_service: str = Header(None)):
    """
    Dependency to verify that the incoming request is from 
    the authorized backend service.
    """
    # 1. Check if the header exists
    if not x_backend_service:
        raise HTTPException(
            status_code=401, 
            detail="Missing security header: x-backend-service"
        )

    # 2. Compare the incoming header with the secret stored in .env
    if x_backend_service != settings.BACKEND_SERVICE_SECRET:
        print(f"SECURITY ALERT: Unauthorized access attempt with key: {x_backend_service}")
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized Backend: Invalid Security Key"
        )

    # 3. If everything is correct, return True to allow the request to proceed
    return True