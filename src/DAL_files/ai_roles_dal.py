from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.ai_roles import AIRole
from schemas.ai_roles_schemas import AIRoleCreate, AIRoleUpdate
from fastapi import HTTPException

class AIRoleDAL:
    async def create_ai_role(self, role_data: AIRoleCreate, db_session: AsyncSession) -> AIRole:
        new_role = AIRole(**role_data.dict())
        db_session.add(new_role)
        await db_session.commit()
        await db_session.refresh(new_role)
        return new_role

    async def get_ai_role_by_id(self, ai_role_id: str, db_session: AsyncSession) -> AIRole:
        return await db_session.get(AIRole, ai_role_id)

    async def get_all_ai_roles(self, db_session: AsyncSession) -> list[AIRole]:
        result = await db_session.execute(select(AIRole))
        return result.scalars().all()

    async def update_ai_role(self, ai_role_id: str, update_data: AIRoleUpdate, db_session: AsyncSession) -> AIRole:
        role = await self.get_ai_role_by_id(ai_role_id, db_session)
        if not role:
            return None
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(role, key, value)
        await db_session.commit()
        await db_session.refresh(role)
        return role

    async def delete_ai_role(self, ai_role_id: str, db_session: AsyncSession) -> bool:
        role = await self.get_ai_role_by_id(ai_role_id, db_session)
        if not role:
            return False
        await db_session.delete(role)
        await db_session.commit()
        return True 