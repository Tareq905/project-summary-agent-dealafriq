from fastapi import Header, HTTPException

async def verify_backend(x_backend_service: str = Header(None)):
    if x_backend_service != "PROJECT_AI_BACKEND":
        raise HTTPException(status_code=401, detail="Unauthorized Backend")
    return True