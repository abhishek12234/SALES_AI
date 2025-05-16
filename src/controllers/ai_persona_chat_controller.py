from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas.ai_persona_chat_schemas import ChatRequest, ChatResponse
from DAL_files.ai_persona_chat_dal import AIPersonaChatDAL
from dependencies import get_current_user
from models.users import User
from DAL_files.sessions_dal import SessionDAL

chat_router = APIRouter()
chat_service = AIPersonaChatDAL()
session_service = SessionDAL()

@chat_router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_persona(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Chat with an AI persona in a specific session.
    The chat will use the interaction mode's prompt template associated with the session,
    combined with the AI persona's attributes to generate responses.
    """
    try:
        # Get the session and validate it belongs to the current user
        chat_session = await session_service.get_session_by_id(str(chat_request.session_id), session)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if chat_session.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this chat session"
            )

        # Validate that the session has a mode_id
        if not chat_session.mode_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat session must have an interaction mode assigned"
            )

        # Process the chat request
        response = await chat_service.process_chat_request(chat_request, session)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the chat request: {str(e)}"
        )
