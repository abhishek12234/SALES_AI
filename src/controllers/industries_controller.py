from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.industries_schemas import IndustryCreate, IndustryUpdate, IndustryResponse
from database import get_session
from DAL_files.industries_dal import IndustryDAL

router = APIRouter()
industry_service = IndustryDAL()

@router.post("/industries/", response_model=IndustryResponse, status_code=status.HTTP_201_CREATED)
async def create_industry(industry: IndustryCreate, session: AsyncSession = Depends(get_session)):
    return await industry_service.create_industry(industry, session)

@router.get("/industries/{industry_id}", response_model=IndustryResponse)
async def get_industry_by_id(industry_id: str, session: AsyncSession = Depends(get_session)):
    industry = await industry_service.get_industry_by_id(industry_id, session)
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return industry

@router.get("/industries/", response_model=list[IndustryResponse])
async def get_all_industries(session: AsyncSession = Depends(get_session)):
    return await industry_service.get_all_industries(session)

@router.put("/industries/{industry_id}", response_model=IndustryResponse)
async def update_industry(industry_id: str, update: IndustryUpdate, session: AsyncSession = Depends(get_session)):
    updated = await industry_service.update_industry(industry_id, update, session)
    if not updated:
        raise HTTPException(status_code=404, detail="Industry not found")
    return updated

@router.delete("/industries/{industry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_industry(industry_id: str, session: AsyncSession = Depends(get_session)):
    success = await industry_service.delete_industry(industry_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Industry not found")
    return 