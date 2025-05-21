from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.plant_size_impacts_schemas import PlantSizeImpactBase, PlantSizeImpactResponse
from database import get_session
from DAL_files.plant_size_impacts_dal import PlantSizeImpactDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

plant_size_impacts_router = APIRouter()
plant_size_impact_service = PlantSizeImpactDAL()

@plant_size_impacts_router.post("/", response_model=PlantSizeImpactResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create_plant_size_impact(
    model: PlantSizeImpactBase,
    session: AsyncSession = Depends(get_session)
):
    existing = await plant_size_impact_service.get_plant_size_impact_by_name(model.name, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plant size impact with this name already exists."
        )
    created = await plant_size_impact_service.create_plant_size_impact(model, session)
    return created

@plant_size_impacts_router.get("/{plant_size_impact_id}", response_model=PlantSizeImpactResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_plant_size_impact_by_id(
    plant_size_impact_id: str,
    session: AsyncSession = Depends(get_session)
):
    model = await plant_size_impact_service.get_plant_size_impact_by_id(plant_size_impact_id, session)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant size impact not found."
        )
    return model

@plant_size_impacts_router.get("/", response_model=list[PlantSizeImpactResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all_plant_size_impacts(
    session: AsyncSession = Depends(get_session)
):
    models = await plant_size_impact_service.get_all_plant_size_impacts(session)
    return models

@plant_size_impacts_router.put("/{plant_size_impact_id}", response_model=PlantSizeImpactResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update_plant_size_impact(
    plant_size_impact_id: str,
    model: PlantSizeImpactBase,
    session: AsyncSession = Depends(get_session)
):
    updated = await plant_size_impact_service.update_plant_size_impact(plant_size_impact_id, model, session)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant size impact not found."
        )
    return updated

@plant_size_impacts_router.delete("/{plant_size_impact_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete_plant_size_impact(
    plant_size_impact_id: str,
    session: AsyncSession = Depends(get_session)
):
    deleted = await plant_size_impact_service.delete_plant_size_impact(plant_size_impact_id, session)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant size impact not found."
        )
    return 