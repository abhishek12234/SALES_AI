from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.persona_produced_product import PersonaProducedProduct
from schemas.persona_produced_product_schemas import PersonaProducedProductBase
import uuid

class PersonaProducedProductDAL:
    async def create_persona_produced_product(self, model: PersonaProducedProductBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = PersonaProducedProduct(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all_persona_produced_products(self, db_session: AsyncSession):
        result = await db_session.execute(select(PersonaProducedProduct))
        return result.scalars().all()

    async def get_persona_produced_product_by_id(self, persona_product_id: str, db_session: AsyncSession):
        result = await db_session.execute(select(PersonaProducedProduct).where(PersonaProducedProduct.persona_product_id == persona_product_id))
        return result.scalar_one_or_none()

    async def update_persona_produced_product(self, persona_product_id: str, model: PersonaProducedProductBase, db_session: AsyncSession):
        db_model = await self.get_persona_produced_product_by_id(persona_product_id, db_session)
        if not db_model:
            return None
        db_model.persona_id = model.persona_id
        db_model.product_id = model.product_id
        await db_session.commit()
        await db_session.refresh(db_model)
        return db_model

    async def delete_persona_produced_product(self, persona_product_id: str, db_session: AsyncSession):
        db_model = await self.get_persona_produced_product_by_id(persona_product_id, db_session)
        if not db_model:
            return False
        await db_session.delete(db_model)
        await db_session.commit()
        return True 