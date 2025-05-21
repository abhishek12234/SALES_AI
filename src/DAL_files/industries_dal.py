from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.industries import Industry
from schemas.industries_schemas import IndustryCreate, IndustryUpdate
from fastapi import HTTPException

class IndustryDAL:
    async def create_industry(self, industry_data: IndustryCreate, db_session: AsyncSession) -> Industry:
        new_industry = Industry(**industry_data.dict())
        db_session.add(new_industry)
        await db_session.commit()
        await db_session.refresh(new_industry)
        return new_industry

    async def get_industry_by_id(self, industry_id: str, db_session: AsyncSession) -> Industry:
        return await db_session.get(Industry, industry_id)

    async def get_all_industries(self, db_session: AsyncSession) -> list[Industry]:
        result = await db_session.execute(select(Industry))
        return result.scalars().all()

    async def update_industry(self, industry_id: str, update_data: IndustryUpdate, db_session: AsyncSession) -> Industry:
        industry = await self.get_industry_by_id(industry_id, db_session)
        if not industry:
            return None
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(industry, key, value)
        await db_session.commit()
        await db_session.refresh(industry)
        return industry

    async def delete_industry(self, industry_id: str, db_session: AsyncSession) -> bool:
        industry = await self.get_industry_by_id(industry_id, db_session)
        if not industry:
            return False
        await db_session.delete(industry)
        await db_session.commit()
        return True 