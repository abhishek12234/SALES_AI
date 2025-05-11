from sqlalchemy.orm import Session
from uuid import UUID
from models.role_permissions import RolePermission
from schemas.role_permissions_schemas import RolePermissionCreate, RolePermissionUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from .roles_dal import RoleDAL

role_dal = RoleDAL()  

class RolePermissionDAL:

    async def create_role_permission(self, permission_data: RolePermissionCreate, db_session: AsyncSession) -> RolePermission:
        # Check if the role exists
        # Initialize RoleDAL with the current session
        if not await role_dal.role_exists(permission_data.role_id,db_session):
            raise ValueError("Role does not exist")

        
        new_permission = RolePermission(
            role_id=permission_data.role_id,
            resource=permission_data.resource,
            action=permission_data.action,
        )
        self.db_session.add(new_permission)
        await self.db_session.flush()
        return new_permission

    async def get_permission_by_id(self, permission_id: str, db_session: AsyncSession) -> RolePermission:
        return await db_session.get(RolePermission, permission_id)

    async def get_permissions_by_role_id(self, role_id: str, db_session: AsyncSession) -> list[RolePermission]:
        result = await db_session.execute(db_session.query(RolePermission).filter(RolePermission.role_id == role_id))
        return result.scalars().all()

    async def update_role_permission(self, permission_id: str, permission_data: RolePermissionUpdate,db_session: AsyncSession) -> RolePermission:
        permission = await self.get_permission_by_id(permission_id, db_session)
        if not permission:
            return None
        for key, value in permission_data.dict(exclude_unset=True).items():
            setattr(permission, key, value)
        await db_session.flush()
        return permission

    async def delete_role_permission(self, permission_id: str,db_session: AsyncSession) -> bool:
        permission = await self.get_permission_by_id(permission_id, db_session)
        if not permission:
            return False
        await self.db_session.delete(permission)
        await self.db_session.flush()
        return True