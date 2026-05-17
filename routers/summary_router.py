from typing import Optional
from fastapi import APIRouter, Depends, Query
from services.session_data_builder import build_session_data
from services.intelligence_orchestrator import (
    analyze_all_projects,
    analyze_all_meetings,
    analyze_all_documents,
)
from services.email_orchestrator import analyze_all_emails
from services.weekly_summary_orchestrator import analyze_and_push_weekly_summaries
from services.client_orchestrator import analyze_all_clients
from api_key_auth import verify_backend

router = APIRouter(prefix="/summary")


@router.post("/project")
async def project_analysis(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    data = build_session_data()
    return analyze_all_projects(data, project_id=id)


@router.post("/weekly-summary")
async def weekly_summary(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    return analyze_and_push_weekly_summaries(project_id=id)


@router.post("/meeting")
async def meeting_analysis(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    data = build_session_data()
    return analyze_all_meetings(data, meeting_id=id)


@router.post("/document")
async def document_analysis(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    data = build_session_data()
    return analyze_all_documents(data, document_id=id)


@router.post("/emails")
async def email_analysis(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    return analyze_all_emails(email_id=id)


@router.post("/clients")
async def client_analysis(
    id: Optional[str] = Query(default=None),
    _ = Depends(verify_backend)
):
    return analyze_all_clients(client_id=id)