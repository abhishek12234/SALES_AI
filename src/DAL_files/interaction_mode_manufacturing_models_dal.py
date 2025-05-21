from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.interaction_mode_manufacturing_models import InteractionModeManufacturingModel
from schemas.interaction_mode_manufacturing_models_schemas import InteractionModeManufacturingModelBase
import uuid

class InteractionModeManufacturingModelDAL:
    async def create(self, model: InteractionModeManufacturingModelBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = InteractionModeManufacturingModel(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all(self, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeManufacturingModel))
        return result.scalars().all()

    async def get_by_id(self, id: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeManufacturingModel).where(InteractionModeManufacturingModel.interaction_mode_manufacturing_model_id == id))
        return result.scalar_one_or_none()

    async def get_by_mode_and_model(self, mode_id: str, manufacturing_model: str, db_session: AsyncSession):
        result = await db_session.execute(select(InteractionModeManufacturingModel).where(InteractionModeManufacturingModel.mode_id == mode_id, InteractionModeManufacturingModel.manufacturing_model == manufacturing_model))
        return result.scalar_one_or_none()

    async def update(self, id: str, model: InteractionModeManufacturingModelBase, db_session: AsyncSession):
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