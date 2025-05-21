from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.manufacturing_models import ManufacturingModel
from schemas.manufacturing_models_schemas import ManufacturingModelCreate, ManufacturingModelUpdate
from fastapi import HTTPException

class ManufacturingModelDAL:
    async def create_manufacturing_model(self, model_data: ManufacturingModelCreate, db_session: AsyncSession) -> ManufacturingModel:
        new_model = ManufacturingModel(**model_data.dict())
        db_session.add(new_model)
        await db_session.commit()
        await db_session.refresh(new_model)
        return new_model

    async def get_manufacturing_model_by_id(self, model_id: str, db_session: AsyncSession) -> ManufacturingModel:
        return await db_session.get(ManufacturingModel, model_id)

    async def get_all_manufacturing_models(self, db_session: AsyncSession) -> list[ManufacturingModel]:
        result = await db_session.execute(select(ManufacturingModel))
        return result.scalars().all()

    async def update_manufacturing_model(self, model_id: str, update_data: ManufacturingModelUpdate, db_session: AsyncSession) -> ManufacturingModel:
        model = await self.get_manufacturing_model_by_id(model_id, db_session)
        if not model:
            return None
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(model, key, value)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    async def delete_manufacturing_model(self, model_id: str, db_session: AsyncSession) -> bool:
        model = await self.get_manufacturing_model_by_id(model_id, db_session)
        if not model:
            return False
        await db_session.delete(model)
        await db_session.commit()
        return True 