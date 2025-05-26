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


performance_reports_router = APIRouter(
    prefix="/performance-reports",
    tags=["Performance Reports"]
)

@performance_reports_router.post("/", response_model=PerformanceReportResponse, status_code=status.HTTP_201_CREATED)
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
    try:
        generated_report = await report_service.generate_performance_report(
            user_id=current_user.user_id,
            session_id=report_data.session_id
        )
        # Convert to dict to ensure proper serialization
        report_dict = {
            "report_id": generated_report.report_id,
            "session_id": generated_report.session_id,
            "overall_score": generated_report.overall_score,
            "engagement_level": generated_report.engagement_level,
            "communication_level": generated_report.communication_level,
            "objection_handling": generated_report.objection_handling,
            "adaptability": generated_report.adaptability,
            "persuasiveness": generated_report.persuasiveness,
            "create_interest": generated_report.create_interest,
            "sale_closing": generated_report.sale_closing,
            "discovery": generated_report.discovery,
            "cross_selling": generated_report.cross_selling,
            "solution_fit": generated_report.solution_fit,
            "coaching_summary": generated_report.coaching_summary,
            "created_at": generated_report.created_at
        }
        return report_dict
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@performance_reports_router.get("/{report_id}", response_model=PerformanceReportResponse, status_code=status.HTTP_200_OK)
async def get_performance_report_by_id(
    report_id: str,
    session: AsyncSession = Depends(get_session)
):
    report_service = PerformanceReportDAL(session)
    report = await report_service.get_performance_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance report not found")
    # Convert to dict to ensure proper serialization
    report_dict = {
        "report_id": report.report_id,
        "session_id": report.session_id,
        "overall_score": report.overall_score,
        "engagement_level": report.engagement_level,
        "communication_level": report.communication_level,
        "objection_handling": report.objection_handling,
        "adaptability": report.adaptability,
        "persuasiveness": report.persuasiveness,
        "create_interest": report.create_interest,
        "sale_closing": report.sale_closing,
        "discovery": report.discovery,
        "cross_selling": report.cross_selling,
        "solution_fit": report.solution_fit,
        "coaching_summary": report.coaching_summary,
        "created_at": report.created_at
    }
    return report_dict

@performance_reports_router.get("/{report_id}/pdf", response_class=StreamingResponse)
async def get_performance_report_pdf(
    report_id: str,
    current_user: UserBase = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_session)
):
    """Generate and return a PDF version of the performance report"""
    try:
        # Initialize DAL
        report_dal = PerformanceReportDAL(db_session)

        # Get the report
        report = await report_dal.get_performance_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Generate PDF
        pdf_generator = PerformanceReportPDFGenerator()
        output_buffer = BytesIO()
        pdf_generator.generate_pdf(report, output_buffer)
        output_buffer.seek(0)

        # Generate filename with timestamp
        filename = f"performance_report_{report.report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

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

# @performance_reports_router.get("/by-session/{session_id}", response_model=list[PerformanceReportResponse], status_code=status.HTTP_200_OK)
# async def get_reports_by_session_id(
#     session_id: str,
#     session: AsyncSession = Depends(get_session)
# ):
#     report_service = PerformanceReportDAL(session)
#     reports = await report_service.get_reports_by_session_id(session_id)
#     return reports

@performance_reports_router.put("/{report_id}", response_model=PerformanceReportResponse, status_code=status.HTTP_200_OK)
async def update_performance_report(
    report_id: str,
    report_update: PerformanceReportUpdate,
    session: AsyncSession = Depends(get_session)
):
    report_service = PerformanceReportDAL(session)
    updated_report = await report_service.update_performance_report(report_id, report_update)
    if not updated_report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance report not found")
    return updated_report

@performance_reports_router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_performance_report(
    report_id: str,
    session: AsyncSession = Depends(get_session)
):
    report_service = PerformanceReportDAL(session)
    success = await report_service.delete_performance_report(report_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance report not found")
    return