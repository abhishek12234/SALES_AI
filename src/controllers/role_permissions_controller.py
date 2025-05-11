from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.role_permissions_schemas import RolePermissionCreate, RolePermissionUpdate, RolePermissionResponse
from database import get_session
from DAL_files.role_permissions_dal import RolePermissionDAL
from dependencies import RoleChecker, get_current_user
from schemas.roles_schemas import RoleEnum

# Only admin and super_admin can manage role permissions
admin_checker = Depends(RoleChecker([RoleEnum.admin, RoleEnum.super_admin]))

role_permissions_router = APIRouter()

@role_permissions_router.post("/", response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED, dependencies=[admin_checker])
async def create_role_permission(
    role_permission: RolePermissionCreate, 
    session: AsyncSession = Depends(get_session)
):
    role_permission_service = RolePermissionDAL(session)
    try:
        created_permission = await role_permission_service.create_role_permission(role_permission)
        return created_permission
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@role_permissions_router.get("/{permission_id}", response_model=RolePermissionResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def get_role_permission_by_id(
    permission_id: str, 
    session: AsyncSession = Depends(get_session)
):
    role_permission_service = RolePermissionDAL(session)
    permission = await role_permission_service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role permission not found")
    return permission

@role_permissions_router.get("/by-role/{role_id}", response_model=list[RolePermissionResponse], status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def get_permissions_by_role_id(
    role_id: str, 
    session: AsyncSession = Depends(get_session)
):
    role_permission_service = RolePermissionDAL(session)
    permissions = await role_permission_service.get_permissions_by_role_id(role_id)
    return permissions

@role_permissions_router.put("/{permission_id}", response_model=RolePermissionResponse, status_code=status.HTTP_200_OK, dependencies=[admin_checker])
async def update_role_permission(
    permission_id: str, 
    role_permission_update: RolePermissionUpdate, 
    session: AsyncSession = Depends(get_session)
):
    role_permission_service = RolePermissionDAL(session)
    updated_permission = await role_permission_service.update_role_permission(permission_id, role_permission_update)
    if not updated_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role permission not found")
    return updated_permission

@role_permissions_router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_checker])
async def delete_role_permission(
    permission_id: str, 
    session: AsyncSession = Depends(get_session)
):
    role_permission_service = RolePermissionDAL(session)
    success = await role_permission_service.delete_role_permission(permission_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role permission not found")
    return