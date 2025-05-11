from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate, PerformanceReportResponse
from database import get_session
from DAL_files.performance_reports_dal import PerformanceReportDAL

performance_reports_router = APIRouter(
    prefix="/performance-reports",
    tags=["Performance Reports"]
)

@performance_reports_router.post("/", response_model=PerformanceReportResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_report(
    report_data: PerformanceReportCreate,
    session: AsyncSession = Depends(get_session)
):
    report_service = PerformanceReportDAL(session)
    try:
        created_report = await report_service.create_performance_report(report_data)
        return created_report
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
    return report

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