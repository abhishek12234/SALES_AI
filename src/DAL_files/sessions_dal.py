from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from models.sessions import Session
from schemas.sessions_schemas import SessionCreate, SessionUpdate
from sqlalchemy.sql import exists
from fastapi import HTTPException
from datetime import datetime, timezone
from models.users import User
from models.ai_personas import AIPersona
from models.interaction_modes import InteractionMode
from .users_dal import UserDAL
from .ai_persona_dal import AIPersonaDAL
from .interaction_modes_dal import InteractionModeDAL
from schemas.sessions_schemas import PersonaData

users_service = UserDAL()
persona_service = AIPersonaDAL()
mode_service = InteractionModeDAL()
class SessionDAL:
    async def session_exists(self, session_id: str, db_session: AsyncSession) -> bool:
        result = await db_session.execute(select(Session).where(Session.session_id == session_id))
        print(f"Session exists: {session_id}", '--------------------------------')
        return result.scalar_one_or_none() is not None

    async def get_all_sessions(self, db_session: AsyncSession) -> list[Session]:
        result = await db_session.execute(select(Session))
        return result.scalars().all()

    async def create_session(self, user_id: str, persona_data: PersonaData, db_session: AsyncSession) -> Session:
        try:
            

            persona_data=persona_data.model_dump()
            mode = await mode_service.get_mode_by_name("closing", db_session)
            if not mode:
                raise HTTPException(status_code=404, detail='Interaction mode not found')
                
            data = {
                "user_id": user_id,
                "ai_persona": persona_data,
                "mode_id": mode.mode_id
            }
            new_session = Session(**data)
            new_session.start_time = datetime.now(timezone.utc)
            db_session.add(new_session)
            await db_session.commit()
            await db_session.refresh(new_session)
            return new_session
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create session: {str(e)}")

    async def get_session_by_id(self, session_id: str, db_session: AsyncSession) -> Session:
        # Check if the session exists

        result = await db_session.execute(select(Session).where(Session.session_id == session_id))
        print(result,"result------------")
        return result.scalar_one_or_none()

    async def get_sessions_by_user_id(self, user_id: str, db_session: AsyncSession) -> list[Session]:
        result = await db_session.execute(
            select(Session).where(Session.user_id == user_id)
        )
        return result.scalars().all()

    async def get_sessions_by_persona_id(self, persona_id: str, db_session: AsyncSession) -> list[Session]:
        result = await db_session.execute(
            select(Session).where(Session.persona_id == persona_id)
        )
        return result.scalars().all()

    async def get_sessions_by_mode_id(self, mode_id: str, db_session: AsyncSession) -> list[Session]:
        result = await db_session.execute(
            select(Session).where(Session.mode_id == mode_id)
        )
        return result.scalars().all()

    async def update_session(self,user_session, session_data: SessionUpdate, db_session: AsyncSession) -> Session:
    
            
        try:
            for key, value in session_data.items():
                setattr(user_session, key, value)
            await db_session.commit()
            await db_session.refresh(user_session)
            return user_session
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update session: {str(e)}")

    async def delete_session(self, session_id: str, db_session: AsyncSession) -> bool:
        session = await self.get_session_by_id(session_id, db_session)
        if not session:
            return False
            
        try:
            await db_session.delete(session)
            await db_session.commit()
            return True
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to delete session: {str(e)}")

    async def get_session_by_id_and_user_id(self, session_id: str, user_id: str, db_session: AsyncSession) -> Session:
        """
        Retrieve a session by both session_id and user_id.
        Returns the Session object if found, otherwise None.
        """
        result = await db_session.execute(
            select(Session).where(Session.session_id == session_id, Session.user_id == user_id)
        )
        return result.scalar_one_or_none()