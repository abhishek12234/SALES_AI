from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.produced_product_category_schemas import ProducedProductCategoryBase, ProducedProductCategoryResponse
from database import get_session
from DAL_files.produced_product_category_dal import ProducedProductCategoryDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

produced_product_category_router = APIRouter()
produced_product_category_service = ProducedProductCategoryDAL()

@produced_product_category_router.post("/", response_model=ProducedProductCategoryResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create_produced_product_category(
    model: ProducedProductCategoryBase,
    session: AsyncSession = Depends(get_session)
):
    existing = await produced_product_category_service.get_produced_product_category_by_name(model.name, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produced product category with this name already exists."
        )
    created = await produced_product_category_service.create_produced_product_category(model, session)
    return created

@produced_product_category_router.get("/{product_id}", response_model=ProducedProductCategoryResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_produced_product_category_by_id(
    product_id: str,
    session: AsyncSession = Depends(get_session)
):
    model = await produced_product_category_service.get_produced_product_category_by_id(product_id, session)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produced product category not found."
        )
    return model

@produced_product_category_router.get("/", response_model=list[ProducedProductCategoryResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all_produced_product_categories(
    session: AsyncSession = Depends(get_session)
):
    models = await produced_product_category_service.get_all_produced_product_categories(session)
    return models

@produced_product_category_router.put("/{product_id}", response_model=ProducedProductCategoryResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update_produced_product_category(
    product_id: str,
    model: ProducedProductCategoryBase,
    session: AsyncSession = Depends(get_session)
):
    updated = await produced_product_category_service.update_produced_product_category(product_id, model, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produced product category not found."
        )
    return updated

@produced_product_category_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete_produced_product_category(
    product_id: str,
    session: AsyncSession = Depends(get_session)
):
    deleted = await produced_product_category_service.delete_produced_product_category(product_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produced product category not found."
        )
    return
