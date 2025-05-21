from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.sessions_schemas import SessionCreate, SessionUpdate, SessionResponse, PersonaData
from database import get_session
from DAL_files.sessions_dal import SessionDAL
from schemas.users_schemas import UserBase
from dependencies import get_current_user

sessions_router = APIRouter()
session_service = SessionDAL()

@sessions_router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    persona_data: PersonaData,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    
    try:
        user_id=current_user.user_id
        created_session = await session_service.create_session(user_id,persona_data,session)
        return created_session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@sessions_router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def get_session_by_id(
    session_id: str,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_id=current_user.user_id
    session_data = await session_service.get_session_by_id_and_user_id(session_id,user_id,session)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Your Session not found")
    return session_data

@sessions_router.get("/by-user/{user_id}", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    
    sessions = await session_service.get_sessions_by_user_id(user_id,session)
    return sessions


@sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    
    success = await session_service.delete_session(session_id,session)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return