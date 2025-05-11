from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from schemas.sessions_schemas import SessionCreate, SessionUpdate, SessionResponse
from database import get_session
from DAL_files.sessions_dal import SessionDAL

sessions_router = APIRouter(
    prefix="/sessions"
)

@sessions_router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    session: AsyncSession = Depends(get_session)
):
    session_service = SessionDAL(session)
    try:
        created_session = await session_service.create_session(session_data)
        return created_session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@sessions_router.get("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def get_session_by_id(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    session_service = SessionDAL(session)
    session_data = await session_service.get_session_by_id(session_id)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session_data

@sessions_router.get("/by-user/{user_id}", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions_by_user_id(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    session_service = SessionDAL(session)
    sessions = await session_service.get_sessions_by_user_id(user_id)
    return sessions

@sessions_router.put("/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    session: AsyncSession = Depends(get_session)
):
    session_service = SessionDAL(session)
    updated_session = await session_service.update_session(session_id, session_update)
    if not updated_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return updated_session

@sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    session_service = SessionDAL(session)
    success = await session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return