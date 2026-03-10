# routers/summary_router.py
from fastapi import APIRouter, Depends
from services.session_data_builder import build_all_sessions_data
from services.intelligence_orchestrator import (
    analyze_all_projects,
    analyze_all_meetings,
    analyze_all_documents,
)
# ADD THIS MISSING LINE BELOW:
from services.email_orchestrator import analyze_all_emails

from api_key_auth import verify_backend

router = APIRouter(prefix="/summary")

@router.post("/project")
async def project_analysis(_ = Depends(verify_backend)):
    data = build_all_sessions_data()
    return analyze_all_projects(data)

@router.post("/meeting")
async def meeting_analysis(_ = Depends(verify_backend)):
    data = build_all_sessions_data()
    return analyze_all_meetings(data)

@router.post("/document")
async def document_analysis(_ = Depends(verify_backend)):
    data = build_all_sessions_data()
    return analyze_all_documents(data)

@router.post("/emails")
async def email_analysis(_ = Depends(verify_backend)):
    return analyze_all_emails()