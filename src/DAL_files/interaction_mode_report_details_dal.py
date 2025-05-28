from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.interaction_mode_report_details import InteractionModeReportDetail
from schemas.interaction_mode_report_details_schemas import InteractionModeReportDetailBase
import uuid

class InteractionModeReportDetailDAL:
    async def create(self, model: InteractionModeReportDetailBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = InteractionModeReportDetail(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all(self, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeReportDetail))
        return result.scalars().all()

    async def get_by_id(self, id: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeReportDetail).where(InteractionModeReportDetail.report_detail_id == id))
        return result.scalar_one_or_none()

    async def get_by_mode_id(self, mode_id: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeReportDetail).where(InteractionModeReportDetail.mode_id == mode_id))
        return result.scalar_one_or_none()

    async def update(self, id: str, model: InteractionModeReportDetailBase, db_session: AsyncSession):
        db_model = await self.get_by_id(id, db_session)
        if not db_model:
            return None
        for key, value in model.model_dump().items():
            setattr(db_model, key, value)
        await db_session.commit()
        await db_session.refresh(db_model)
        return db_model

    async def delete(self, id: str, db_session: AsyncSession):
        db_model = await self.get_by_id(id, db_session)
        if not db_model:
            return False
        await db_session.delete(db_model)
        await db_session.commit()
        return True 