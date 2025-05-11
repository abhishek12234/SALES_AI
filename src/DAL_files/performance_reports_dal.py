from sqlalchemy.orm import Session
from uuid import UUID
from models.performance_reports import PerformanceReport
from schemas.performance_reports_schemas import PerformanceReportCreate, PerformanceReportUpdate

class PerformanceReportDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_performance_report(self, report_data: PerformanceReportCreate) -> PerformanceReport:
        new_report = PerformanceReport(
            session_id=report_data.session_id,
            overall_score=report_data.overall_score,
            engagement_level=report_data.engagement_level,
            communication_level=report_data.communication_level,
            objection_handling=report_data.objection_handling,
            adaptability=report_data.adaptability,
            persuasiveness=report_data.persuasiveness,
            create_interest=report_data.create_interest,
            sale_closing=report_data.sale_closing,
            discovery=report_data.discovery,
            cross_selling=report_data.cross_selling,
            solution_fit=report_data.solution_fit,
            coaching_summary=report_data.coaching_summary,
        )
        self.db_session.add(new_report)
        await self.db_session.flush()
        return new_report

    async def get_performance_report_by_id(self, report_id: str) -> PerformanceReport:
        return await self.db_session.get(PerformanceReport, report_id)

    # async def get_reports_by_session_id(self, session_id: str) -> list[PerformanceReport]:
    #     result = await self.db_session.execute(
    #         self.db_session.query(PerformanceReport).filter(PerformanceReport.session_id == session_id)
    #     )
    #     return result.scalars().all()

    async def update_performance_report(self, report_id: str, report_data: PerformanceReportUpdate) -> PerformanceReport:
        report = await self.get_performance_report_by_id(report_id)
        if not report:
            return None
        for key, value in report_data.dict(exclude_unset=True).items():
            setattr(report, key, value)
        await self.db_session.flush()
        return report

    async def delete_performance_report(self, report_id: str) -> bool:
        report = await self.get_performance_report_by_id(report_id)
        if not report:
            return False
        await self.db_session.delete(report)
        await self.db_session.flush()
        return True