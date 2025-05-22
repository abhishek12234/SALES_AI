from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.interaction_mode_plant_size_impacts_schemas import InteractionModePlantSizeImpactBase, InteractionModePlantSizeImpactResponse
from database import get_session
from DAL_files.interaction_mode_plant_size_impacts_dal import InteractionModePlantSizeImpactDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

interaction_mode_plant_size_impacts_router = APIRouter()
service = InteractionModePlantSizeImpactDAL()

@interaction_mode_plant_size_impacts_router.post("/", response_model=InteractionModePlantSizeImpactResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create(model: InteractionModePlantSizeImpactBase, session: AsyncSession = Depends(get_session)):
    existing = await service.get_by_mode_and_impact(model.mode_id, model.plant_size_impact_id, session)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entry with this mode and plant size impact already exists.")
    created = await service.create(model, session)
    return created

@interaction_mode_plant_size_impacts_router.get("/{id}", response_model=InteractionModePlantSizeImpactResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_by_id(id: str, session: AsyncSession = Depends(get_session)):
    obj = await service.get_by_id(id, session)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return obj

@interaction_mode_plant_size_impacts_router.get("/", response_model=list[InteractionModePlantSizeImpactResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all(session: AsyncSession = Depends(get_session)):
    return await service.get_all(session)

@interaction_mode_plant_size_impacts_router.put("/{id}", response_model=InteractionModePlantSizeImpactResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update(id: str, model: InteractionModePlantSizeImpactBase, session: AsyncSession = Depends(get_session)):
    updated = await service.update(id, model, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return updated

@interaction_mode_plant_size_impacts_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete(id: str, session: AsyncSession = Depends(get_session)):
    deleted = await service.delete(id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return 