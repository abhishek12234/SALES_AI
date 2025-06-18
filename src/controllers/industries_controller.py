from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.industries_schemas import IndustryCreate, IndustryUpdate, IndustryResponse
from database import get_session
from DAL_files.industries_dal import IndustryDAL
import loggingHello, this is an  message! for adding a s
from sqlalchemy.exc import IntegrityError
from dependencies import RoleChecker
from schemas.roles_schemas import RoleEnum

industry_router = APIRouter()
industry_service = IndustryDAL()
logger = logging.getLogger("industries")

admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

@industry_router.post("/", response_model=IndustryResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_industry(industry: IndustryCreate, session: AsyncSession = Depends(get_session)):
    try:
        return await industry_service.create_industry(industry, session)
    except IntegrityError as e:
        logger.exception("Integrity error while creating industry")
        # Check for duplicate entry (unique constraint)
        if "Duplicate entry" in str(e.orig):
            raise HTTPException(status_code=400, detail="Industry with this name already exists.")
        elif "cannot be null" in str(e.orig):
            raise HTTPException(status_code=400, detail="A required field is missing.")
        elif "foreign key constraint fails" in str(e.orig):
            raise HTTPException(status_code=400, detail="Invalid reference to another table.")
        else:
            raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        logger.exception("Failed to create industry")
        raise HTTPException(status_code=500, detail="Internal server error")

@industry_router.get("/{industry_id}", response_model=IndustryResponse, dependencies=[manager_checker])
async def get_industry_by_id(industry_id: str, session: AsyncSession = Depends(get_session)):
    try:
        industry = await industry_service.get_industry_by_id(industry_id, session)
        if not industry:
            raise HTTPException(status_code=404, detail="Industry not found")
        return industry
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get industry by id")
        raise HTTPException(status_code=500, detail="Internal server error")

@industry_router.get("/", response_model=list[IndustryResponse], dependencies=[manager_checker])
async def get_all_industries(session: AsyncSession = Depends(get_session)):
    try:
        return await industry_service.get_all_industries(session)
    except Exception as e:
        logger.exception("Failed to get all industries")
        raise HTTPException(status_code=500, detail="Internal server error")

@industry_router.put("/{industry_id}", response_model=IndustryResponse, dependencies=[admin_checker])
async def update_industry(industry_id: str, update: IndustryUpdate, session: AsyncSession = Depends(get_session)):
    try:
        updated = await industry_service.update_industry(industry_id, update, session)
        if not updated:
            raise HTTPException(status_code=404, detail="Industry not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update industry")
        raise HTTPException(status_code=500, detail="Internal server error")

@industry_router.delete("/{industry_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_industry(industry_id: str, session: AsyncSession = Depends(get_session)):
    try:
        success = await industry_service.delete_industry(industry_id, session)
        if not success:
            raise HTTPException(status_code=404, detail="Industry not found")
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete industry")
        raise HTTPException(status_code=500, detail="Internal server error") 