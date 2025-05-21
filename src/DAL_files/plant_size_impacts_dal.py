from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.plant_size_impacts import PlantSizeImpact
from schemas.plant_size_impacts_schemas import PlantSizeImpactBase
import uuid

class PlantSizeImpactDAL:
    async def create_plant_size_impact(self, model: PlantSizeImpactBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = PlantSizeImpact(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all_plant_size_impacts(self, db_session: AsyncSession):
        result = await db_session.execute(select(PlantSizeImpact))
        return result.scalars().all()

    async def get_plant_size_impact_by_id(self, plant_size_impact_id: str, db_session: AsyncSession):
        result = await db_session.execute(select(PlantSizeImpact).where(PlantSizeImpact.plant_size_impact_id == plant_size_impact_id))
        return result.scalar_one_or_none()

    async def get_plant_size_impact_by_name(self, name: str, db_session: AsyncSession):
        result = await db_session.execute(select(PlantSizeImpact).where(PlantSizeImpact.name == name))
        return result.scalar_one_or_none()

    async def update_plant_size_impact(self, plant_size_impact_id: str, model: PlantSizeImpactBase, db_session: AsyncSession):
        db_model = await self.get_plant_size_impact_by_id(plant_size_impact_id, db_session)
        if not db_model:
            return None
        db_model.name = model.name
        await db_session.commit()
        await db_session.refresh(db_model)
        return db_model

    async def delete_plant_size_impact(self, plant_size_impact_id: str, db_session: AsyncSession):
        db_model = await self.get_plant_size_impact_by_id(plant_size_impact_id, db_session)
        if not db_model:
            return False
        await db_session.delete(db_model)
        await db_session.commit()
        return True 