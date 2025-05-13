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

    async def create_session(self, session_data: SessionCreate, db_session: AsyncSession) -> Session:
        try:
            
            # Validate user_id
           
            user = await users_service.get_user_by_id(session_data.user_id, db_session)
            if not user:
                raise HTTPException(status_code=404, detail='User not found')
            # Validate persona_id if provided
            
            persona_id = session_data.persona_id
            if persona_id is not None:
                persona = await persona_service.get_ai_persona_by_id(persona_id, db_session)
                if not persona:
                    raise HTTPException(status_code=404, detail='Persona not found')
            # Validate mode_id if provided
       
            mode_id = session_data.mode_id
            if mode_id is not None:
                mode = await mode_service.get_mode_by_id(mode_id, db_session)
                if not mode:
                    raise HTTPException(status_code=404, detail='Interaction mode not found')
                
            data = session_data.model_dump()
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
        exists = await self.session_exists(session_id, db_session)
        if not exists:
            return None

        return await db_session.get(Session, session_id)

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

    async def update_session(self, session_id: str, session_data: SessionUpdate, db_session: AsyncSession) -> Session:
        session = await self.get_session_by_id(session_id, db_session)
        if not session:
            return None
            
        try:
            for key, value in session_data.model_dump(exclude_unset=True).items():
                setattr(session, key, value)
            await db_session.commit()
            await db_session.refresh(session)
            return session
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