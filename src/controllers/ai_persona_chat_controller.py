from fastapi import APIRouter, HTTPException
from DAL_files.ai_persona_chat_dal import AIPersonaChatDAL
import uuid
from langchain_groq import ChatGroq
from schemas.users_schemas import UserBase
from fastapi import Depends
from dependencies import get_current_user
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from DAL_files.sessions_dal import SessionDAL
from schemas.ai_personas_chat_schemas import ChatWithPersonaRequest
from redis_store import get_prompt_template
from pydantic import BaseModel
from typing import Optional


ai_persona_chat_router = APIRouter()
ai_persona_chat_service = AIPersonaChatDAL()
session_services = SessionDAL()



class ChatRequest(BaseModel):
    user_input: str
    thought: Optional[str] = None 

@ai_persona_chat_router.post("/chat/{session_id}")
async def chat_with_persona(
    session_id: str,
    chat_request: ChatRequest,
    current_user: UserBase = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        user_session=await session_services.get_session_by_id_and_user_id(session_id,current_user.user_id,session)  
        if user_session is None:
            raise HTTPException(status_code=404, detail="Session not found. Create a new session first.")
        
        await session_services.update_session(user_session, {"status":"active"}, session)
        
        user_id = current_user.user_id
        
        # Fetch the prompt template from Redis
        persona_prompt = await get_prompt_template(user_id, session_id)
        if not persona_prompt:
            raise HTTPException(status_code=404, detail="Prompt template not found in Redis.")
   
        user_input = chat_request.user_input
        response = await ai_persona_chat_service.chat_with_persona(session_id, user_id, persona_prompt, user_input)

        return {"response":response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
