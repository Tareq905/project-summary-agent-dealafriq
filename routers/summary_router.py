from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from services.session_data_builder import build_session_data
from services.intelligence_orchestrator import (
    analyze_all_projects,
    analyze_all_meetings,
    analyze_all_documents,
)
from services.email_orchestrator import analyze_all_emails
from services.weekly_summary_orchestrator import analyze_and_push_weekly_summaries
from services.client_orchestrator import analyze_all_clients
from services.email_draft_orchestrator import generate_email_draft
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


@router.post("/email-draft")
async def email_draft(
    id: str = Query(..., description="The ID of the email to generate or regenerate a draft for."),
    _ = Depends(verify_backend)
):
    """
    Generate or regenerate a professional email draft for a specific email.
 
    - Always produces a fresh draft — safe to call repeatedly (regenerate).
    - Fetches the email by ID, generates a structured reply draft using AI,
      and pushes the result to the backend.
 
    **Request:**
    - Method: POST
    - Query param: `?id=<emailId>`
    - Header: `x-backend-service: <secret>`
 
    **Response:**
    ```json
    {
        "success": true,
        "emailId": "abc123",
        "pushed": true,
        "draft": {
            "subject": "Re: ...",
            "greeting": "Dear Robert,",
            "opening": "...",
            "body": "...",
            "closing": "...",
            "sign_off": "Best regards,",
            "signature": "[Your Name]\\n[Your Title]\\n[Your Company]",
            "full_draft": "...",
            "intent_tag": "Acknowledgement",
            "urgency": "High",
            "key_points_addressed": ["...", "..."]
        },
        "meta": {
            "original_subject": "...",
            "sender": "...",
            "sender_email": "...",
            "received_at": "..."
        }
    }
    ```
    """
    if not id or not id.strip():
        raise HTTPException(status_code=400, detail="Email ID is required. Use ?id=<emailId>")
 
    result = generate_email_draft(email_id=id.strip())
 
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=result.get("error", "Email draft generation failed.")
        )
 
    # Return only success, emailId, and draft
    return {
        "success": result.get("success"),
        "emailId": result.get("emailId"),
        "draft":   result.get("draft")
    }