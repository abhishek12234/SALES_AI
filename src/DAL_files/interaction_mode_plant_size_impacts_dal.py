from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.interaction_mode_plant_size_impacts import InteractionModePlantSizeImpact
from schemas.interaction_mode_plant_size_impacts_schemas import InteractionModePlantSizeImpactBase
import uuid

class InteractionModePlantSizeImpactDAL:
    async def create(self, model: InteractionModePlantSizeImpactBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = InteractionModePlantSizeImpact(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all(self, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModePlantSizeImpact))
        return result.scalars().all()

    async def get_by_id(self, id: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModePlantSizeImpact).where(InteractionModePlantSizeImpact.interaction_mode_plant_size_impact_id == id))
        return result.scalar_one_or_none()

    async def get_by_mode_and_impact(self, mode_id: str, plant_size_impact: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModePlantSizeImpact).where(InteractionModePlantSizeImpact.mode_id == mode_id, InteractionModePlantSizeImpact.plant_size_impact == plant_size_impact))
        return result.scalar_one_or_none()

    async def update(self, id: str, model: InteractionModePlantSizeImpactBase, db_session: AsyncSession):
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