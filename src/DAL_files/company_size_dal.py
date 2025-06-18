from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from models.company_size import CompanySize
from schemas.company_size_schemas import CompanySizeBase
import uuid

class CompanySizeDAL:
    async def create_company_size(self, model: CompanySizeBase, db_session: AsyncSession):
        model = model.model_dump()
        new_model = CompanySize(**model)
        db_session.add(new_model)
        try:
            await db_session.commit()
            await db_session.refresh(new_model)
            return new_model
        except IntegrityError:
            await db_session.rollback()
            raise 

    async def get_all_company_sizes(self, db_session: AsyncSession):
        result = await db_session.execute(select(CompanySize))
        return result.scalars().all()

    async def get_company_size_by_id(self, company_size_id: str, db_session: AsyncSession):
        result = await db_session.execute(select(CompanySize).where(CompanySize.company_size_id == company_size_id))
        return result.scalar_one_or_none()

    async def get_company_size_by_name(self, name: str, db_session: AsyncSession):
        result = await db_session.execute(select(CompanySize).where(CompanySize.name == name))
        return result.scalar_one_or_none()

    async def update_company_size(self, company_size_id: str, model: CompanySizeBase, db_session: AsyncSession):
        db_model = await self.get_company_size_by_id(company_size_id, db_session)
        if not db_model:
            return None
        db_model.name = model.name
        db_model.description = model.description
        await db_session.commit()
        await db_session.refresh(db_model)
        return db_model

    async def delete_company_size(self, company_size_id: str, db_session: AsyncSession):
        db_model = await self.get_company_size_by_id(company_size_id, db_session)
        if not db_model:
            return False
        await db_session.delete(db_model)
        await db_session.commit()
        return True 