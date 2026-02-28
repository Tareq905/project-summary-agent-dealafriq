from fastapi import APIRouter
from services.session_data_builder import build_session_data
from services.unified_summary_builder import build_unified_summary

router = APIRouter(prefix="/summary")

@router.post("/session")
async def session_summary(session: str):
    session = session.upper()
    session_data = build_session_data(session)
    result = build_unified_summary(session_data)
    return {session: result}