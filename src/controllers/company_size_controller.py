from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.company_size_schemas import CompanySizeBase, CompanySizeResponse
from database import get_session
from DAL_files.company_size_dal import CompanySizeDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

company_size_router = APIRouter()
company_size_service = CompanySizeDAL()

@company_size_router.post("/", response_model=CompanySizeResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create_company_size(
    model: CompanySizeBase,
    session: AsyncSession = Depends(get_session)
):
    existing = await company_size_service.get_company_size_by_name(model.name, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company size with this name already exists."
        )
    created = await company_size_service.create_company_size(model, session)
    return created

@company_size_router.get("/{company_size_id}", response_model=CompanySizeResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_company_size_by_id(
    company_size_id: str,
    session: AsyncSession = Depends(get_session)
):
    model = await company_size_service.get_company_size_by_id(company_size_id, session)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company size not found."
        )
    return model

@company_size_router.get("/", response_model=list[CompanySizeResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all_company_sizes(
    session: AsyncSession = Depends(get_session)
):
    models = await company_size_service.get_all_company_sizes(session)
    return models

@company_size_router.put("/{company_size_id}", response_model=CompanySizeResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update_company_size(
    company_size_id: str,
    model: CompanySizeBase,
    session: AsyncSession = Depends(get_session)
):
    updated = await company_size_service.update_company_size(company_size_id, model, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company size not found."
        )
    return updated

@company_size_router.delete("/{company_size_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete_company_size(
    company_size_id: str,
    session: AsyncSession = Depends(get_session)
):
    deleted = await company_size_service.delete_company_size(company_size_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company size not found."
        )
    return 