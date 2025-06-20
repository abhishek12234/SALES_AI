from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.persona_produced_product_schemas import (
    PersonaProducedProductBase, PersonaProducedProductResponse
)
from database import get_session
from DAL_files.persona_produced_product_dal import PersonaProducedProductDAL
from dependencies import RoleChecker
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

persona_produced_product_router = APIRouter()
persona_produced_product_service = PersonaProducedProductDAL()

@persona_produced_product_router.post("/", response_model=PersonaProducedProductResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create_persona_produced_product(
    model: PersonaProducedProductBase,
    session: AsyncSession = Depends(get_session)
):
    created = await persona_produced_product_service.create_persona_produced_product(model, session)
    return created

@persona_produced_product_router.get("/{persona_product_id}", response_model=PersonaProducedProductResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_persona_produced_product_by_id(
    persona_product_id: str,
    session: AsyncSession = Depends(get_session)
):
    model = await persona_produced_product_service.get_persona_produced_product_by_id(persona_product_id, session)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona produced product not found."
        )
    return model

@persona_produced_product_router.get("/", response_model=list[PersonaProducedProductResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all_persona_produced_products(
    session: AsyncSession = Depends(get_session)
):
    models = await persona_produced_product_service.get_all_persona_produced_products(session)
    return models

@persona_produced_product_router.put("/{persona_product_id}", response_model=PersonaProducedProductResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update_persona_produced_product(
    persona_product_id: str,
    model: PersonaProducedProductBase,
    session: AsyncSession = Depends(get_session)
):
    updated = await persona_produced_product_service.update_persona_produced_product(persona_product_id, model, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona produced product not found."
        )
    return updated

@persona_produced_product_router.delete("/{persona_product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete_persona_produced_product(
    persona_product_id: str,
    session: AsyncSession = Depends(get_session)
):
    deleted = await persona_produced_product_service.delete_persona_produced_product(persona_product_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona produced product not found."
        )
    return 