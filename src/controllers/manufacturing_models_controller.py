from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.manufacturing_models_schemas import ManufacturingModelCreate, ManufacturingModelUpdate, ManufacturingModelResponse
from database import get_session
from DAL_files.manufacturing_models_dal import ManufacturingModelDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))

manufacturing_models_router = APIRouter()
service = ManufacturingModelDAL()

@manufacturing_models_router.post("/", response_model=ManufacturingModelResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create(model: ManufacturingModelCreate, session: AsyncSession = Depends(get_session)):
    created = await service.create_manufacturing_model(model, session)
    return created

@manufacturing_models_router.get("/{model_id}", response_model=ManufacturingModelResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_by_id(model_id: str, session: AsyncSession = Depends(get_session)):
    obj = await service.get_manufacturing_model_by_id(model_id, session)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return obj

@manufacturing_models_router.get("/", response_model=list[ManufacturingModelResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all(session: AsyncSession = Depends(get_session)):
    return await service.get_all_manufacturing_models(session)

@manufacturing_models_router.put("/{model_id}", response_model=ManufacturingModelResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update(model_id: str, model: ManufacturingModelUpdate, session: AsyncSession = Depends(get_session)):
    updated = await service.update_manufacturing_model(model_id, model, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return updated

@manufacturing_models_router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete(model_id: str, session: AsyncSession = Depends(get_session)):
    deleted = await service.delete_manufacturing_model(model_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return 