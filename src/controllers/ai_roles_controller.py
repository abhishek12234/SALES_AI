from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.ai_roles_schemas import AIRoleCreate, AIRoleUpdate, AIRoleResponse
from database import get_session
from DAL_files.ai_roles_dal import AIRoleDAL

ai_role_router = APIRouter()
ai_role_service = AIRoleDAL()

@ai_role_router.post("/", response_model=AIRoleResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_role(role: AIRoleCreate, session: AsyncSession = Depends(get_session)):
    return await ai_role_service.create_ai_role(role, session)

@ai_role_router.get("/{ai_role_id}", response_model=AIRoleResponse)
async def get_ai_role_by_id(ai_role_id: str, session: AsyncSession = Depends(get_session)):
    role = await ai_role_service.get_ai_role_by_id(ai_role_id, session)
    if not role:
        raise HTTPException(status_code=404, detail="AI Role not found")
    return role

@ai_role_router.get("/", response_model=list[AIRoleResponse])
async def get_all_ai_roles(session: AsyncSession = Depends(get_session)):
    return await ai_role_service.get_all_ai_roles(session)

@ai_role_router.put("/{ai_role_id}", response_model=AIRoleResponse)
async def update_ai_role(ai_role_id: str, update: AIRoleUpdate, session: AsyncSession = Depends(get_session)):
    updated = await ai_role_service.update_ai_role(ai_role_id, update, session)
    if not updated:
        raise HTTPException(status_code=404, detail="AI Role not found")
    return updated

@ai_role_router.delete("/{ai_role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_role(ai_role_id: str, session: AsyncSession = Depends(get_session)):
    success = await ai_role_service.delete_ai_role(ai_role_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="AI Role not found")
    return 