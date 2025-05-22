from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.industries_schemas import IndustryCreate, IndustryUpdate, IndustryResponse
from database import get_session
from DAL_files.industries_dal import IndustryDAL

industry_router = APIRouter()
industry_service = IndustryDAL()

@industry_router.post("/", response_model=IndustryResponse, status_code=status.HTTP_201_CREATED)
async def create_industry(industry: IndustryCreate, session: AsyncSession = Depends(get_session)):
    return await industry_service.create_industry(industry, session)

@industry_router.get("/{industry_id}", response_model=IndustryResponse)
async def get_industry_by_id(industry_id: str, session: AsyncSession = Depends(get_session)):
    industry = await industry_service.get_industry_by_id(industry_id, session)
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return industry

@industry_router.get("/", response_model=list[IndustryResponse])
async def get_all_industries(session: AsyncSession = Depends(get_session)):
    return await industry_service.get_all_industries(session)

@industry_router.put("/{industry_id}", response_model=IndustryResponse)
async def update_industry(industry_id: str, update: IndustryUpdate, session: AsyncSession = Depends(get_session)):
    updated = await industry_service.update_industry(industry_id, update, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Industry not found")
    return updated

@industry_router.delete("/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_industry(industry_id: str, session: AsyncSession = Depends(get_session)):
    success = await industry_service.delete_industry(industry_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Industry not found")
    return 