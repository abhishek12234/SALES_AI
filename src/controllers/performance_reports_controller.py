from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate, PerformanceReportResponse
from database import get_session
from DAL_files.performance_reports_dal import PerformanceReportDAL
from DAL_files.sessions_dal import SessionDAL
from schemas.users_schemas import UserBase
from dependencies import get_current_user
from pydantic import BaseModel
from typing import Dict, Any, List
from io import BytesIO
from datetime import datetime
from services.pdf_generator import PerformanceReportPDFGenerator
from DAL_files.interaction_mode_report_details_dal import InteractionModeReportDetailDAL
from DAL_files.sessions_dal import SessionDAL


performance_reports_router = APIRouter()

interaction_mode_report_service = InteractionModeReportDetailDAL()
session_service = SessionDAL()

@performance_reports_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_performance_report(
    report_data: PerformanceReportCreate,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new performance report by analyzing the chat history for a given session.
    The request body must include user_id and session_id.
    """
    # Generate the report from chat history
    report_service = PerformanceReportDAL(session)
    session_data = await session_service.get_session_by_id(report_data.session_id, session)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session_data.performance_report:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Performance report already exists")

    interaction_mode_report = await interaction_mode_report_service.get_by_mode_id(session_data.mode_id, session)
    if not interaction_mode_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction mode report not found")
    
    try:
        generated_report = await report_service.generate_performance_report(
            user_id=current_user.user_id,
            session_id=report_data.session_id,
            prompt_template=interaction_mode_report.prompt_template
        )
        # Convert to dict to ensure proper serialization
        await session_service.update_session(session_data, {"performance_report": generated_report}, session)
        return generated_report
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@performance_reports_router.get("/{session_id}", status_code=status.HTTP_200_OK)
async def get_performance_report_by_id(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_id = current_user.user_id
    report_service = PerformanceReportDAL(session)
    report= await report_service.get_performance_report_by_user_session(session_id, user_id)
    return report

@performance_reports_router.get("/{session_id}/pdf", response_class=StreamingResponse)
async def get_performance_report_pdf(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_session)
):
    """Generate and return a PDF version of the performance report"""
    try:
        # Initialize DAL
        report_dal = PerformanceReportDAL(db_session)
        user_id = current_user.user_id
        # Get the report
        report = await report_dal.get_performance_report_by_user_session(session_id, user_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Convert dict to Pydantic model if needed
        if isinstance(report, dict):
            report.setdefault("session_id", session_id)
            report.setdefault("report_id", "N/A")
            report.setdefault("created_at", datetime.now())
            report.setdefault("updated_at", datetime.now())
            report = PerformanceReportResponse(**report)

        # Generate PDF
        pdf_generator = PerformanceReportPDFGenerator()
        output_buffer = BytesIO()
        pdf_generator.generate_pdf(report, output_buffer)
        output_buffer.seek(0)

        # Generate filename with timestamp
        filename = f"performance_report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Return PDF as streaming response
        return StreamingResponse(
            output_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")



