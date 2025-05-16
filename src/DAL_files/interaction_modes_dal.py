from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.interaction_modes import InteractionMode
from schemas.interaction_modes_schemas import InteractionModeCreate, InteractionModeUpdate
from sqlalchemy.sql import exists
from fastapi import HTTPException

class InteractionModeDAL:
    
    async def mode_exists(self, mode_id: str, db_session: AsyncSession) -> bool:
        result = await db_session.execute(select(InteractionMode).where(InteractionMode.mode_id == mode_id))
        print(f"Mode exists: {mode_id}", '--------------------------------')
        return result.scalar_one_or_none() is not None

    async def get_all_modes(self, db_session: AsyncSession) -> list[InteractionMode]:
        result = await db_session.execute(select(InteractionMode))
        return result.scalars().all()

    async def get_modes_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[InteractionMode]:
        """
        Get all interaction modes associated with a specific user
        """
        try:
            result = await db_session.execute(
                select(InteractionMode)
                .where(InteractionMode.user_id == user_id)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to get interaction modes for user: {str(e)}")

    async def create_mode(self, mode_data: InteractionModeCreate, db_session: AsyncSession) -> InteractionMode:
        try:
            mode_data=mode_data.model_dump()
            new_mode = InteractionMode(**mode_data)
            
            db_session.add(new_mode)
            await db_session.commit()
            await db_session.refresh(new_mode)
            return new_mode
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create interaction mode: {str(e)}")

    async def get_mode_by_id(self, mode_id: str, db_session: AsyncSession) -> InteractionMode:
        # Check if the mode exists
        exists = await self.mode_exists(mode_id, db_session)
        if not exists:
            return None

        return await db_session.get(InteractionMode, mode_id)

    async def get_mode_by_name(self, name: str, db_session: AsyncSession) -> InteractionMode:
        result = await db_session.execute(
            select(InteractionMode).where(InteractionMode.name == name)
        )
        return result.scalar_one_or_none()

    async def update_mode(self, mode_id: str, mode_data: InteractionModeUpdate, db_session: AsyncSession) -> InteractionMode:
        mode = await self.get_mode_by_id(mode_id, db_session)
        if not mode:
            return None
            
        try:
            for key, value in mode_data.model_dump(exclude_unset=True).items():
                setattr(mode, key, value)
            await db_session.commit()
            await db_session.refresh(mode)
            return mode
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update interaction mode: {str(e)}")

    async def delete_mode(self, mode_id: str, db_session: AsyncSession) -> bool:
        mode = await self.get_mode_by_id(mode_id, db_session)
        if not mode:
            return False
            
        try:
            await db_session.delete(mode)
            await db_session.commit()
            return True
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete interaction mode: {str(e)}")