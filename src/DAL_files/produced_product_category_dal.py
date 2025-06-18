from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.produced_product_category import ProducedProductCategory
from schemas.produced_product_category_schemas import ProducedProductCategoryBase
import uuid

class ProducedProductCategoryDAL:
    async def create_produced_product_category(self, model: ProducedProductCategoryBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = ProducedProductCategory(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise

    async def get_all_produced_product_categories(self, db_session: AsyncSession):
        result = await db_session.execute(select(ProducedProductCategory))
        return result.scalars().all()

    async def get_produced_product_category_by_id(self, product_id: str, db_session: AsyncSession):
        result = await db_session.execute(select(ProducedProductCategory).where(ProducedProductCategory.product_id == product_id))
        return result.scalar_one_or_none()

    async def get_produced_product_category_by_name(self, name: str, db_session: AsyncSession):
        result = await db_session.execute(select(ProducedProductCategory).where(ProducedProductCategory.name == name))
        return result.scalar_one_or_none()

    async def update_produced_product_category(self, product_id: str, model: ProducedProductCategoryBase, db_session: AsyncSession):
        db_model = await self.get_produced_product_category_by_id(product_id, db_session)
        if not db_model:
            return None
        db_model.industry_id = model.industry_id
        db_model.name = model.name
        db_model.details = model.details
        await db_session.commit()
        await db_session.refresh(db_model)
        return db_model

    async def delete_produced_product_category(self, product_id: str, db_session: AsyncSession):
        db_model = await self.get_produced_product_category_by_id(product_id, db_session)
        if not db_model:
            return False
        await db_session.delete(db_model)
        await db_session.commit()
        return True
