from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.interaction_mode_ai_roles_schemas import InteractionModeAIRoleBase, InteractionModeAIRoleResponse
from database import get_session
from DAL_files.interaction_mode_ai_roles_dal import InteractionModeAIRoleDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum
import logging

logger = logging.getLogger("interaction_mode_ai_roles")
super_admin_checker = Depends(RoleChecker([RoleEnum.super_admin]))
manager_checker = Depends(RoleChecker([RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))
sales_checker = Depends(RoleChecker([RoleEnum.sales_person, RoleEnum.manager, RoleEnum.admin, RoleEnum.super_admin]))

interaction_mode_ai_roles_router = APIRouter()
service = InteractionModeAIRoleDAL()

@interaction_mode_ai_roles_router.post("/", response_model=InteractionModeAIRoleResponse, status_code=status.HTTP_201_CREATED, dependencies=[super_admin_checker])
async def create(model: InteractionModeAIRoleBase, session: AsyncSession = Depends(get_session)):
    try:
        existing = await service.get_by_mode_and_role(model.mode_id, model.ai_role_id, session)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Entry with this mode and ai_role already exists.")
        created = await service.create(model, session)
        return created
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create interaction mode ai role")
        raise HTTPException(status_code=500, detail=str(e))

@interaction_mode_ai_roles_router.get("/{id}", response_model=InteractionModeAIRoleResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_by_id(id: str, session: AsyncSession = Depends(get_session)):
    obj = await service.get_by_id(id, session)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return obj

@interaction_mode_ai_roles_router.get("/", response_model=list[InteractionModeAIRoleResponse], status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def get_all(session: AsyncSession = Depends(get_session)):
    return await service.get_all(session)

@interaction_mode_ai_roles_router.put("/{id}", response_model=InteractionModeAIRoleResponse, status_code=status.HTTP_200_OK, dependencies=[super_admin_checker])
async def update(id: str, model: InteractionModeAIRoleBase, session: AsyncSession = Depends(get_session)):
    updated = await service.update(id, model, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return updated

@interaction_mode_ai_roles_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[super_admin_checker])
async def delete(id: str, session: AsyncSession = Depends(get_session)):
    deleted = await service.delete(id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    return 