from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from models.sessions import Session
from models.ai_personas import AIPersona
from models.interaction_modes import InteractionMode
from models.chat_messages import ChatMessage
from schemas.ai_persona_chat_schemas import ChatMessageCreate, ChatRequest, ChatResponse
from fastapi import HTTPException
from datetime import datetime
import uuid
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from config import settings
import json
import re
from .sessions_dal import SessionDAL
from .ai_persona_dal import AIPersonaDAL
from .interaction_modes_dal import InteractionModeDAL
from constants.industry_details import (
    INDUSTRY_DETAILS,
    ROLE_DETAILS,
    EXPERIENCE_LEVEL_DETAILS,
    MANUFACTURING_MODEL_DETAILS,
    GEOGRAPHY_DETAILS
)

class AIPersonaChatDAL:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="meta-llama/llama-3.3-70b-instruct:free",
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/your-repo",  # Required for OpenRouter
                "X-Title": "Sales AI"  # Optional, but helps OpenRouter track usage
            }
        )
        self.session_service = SessionDAL()
        self.persona_service = AIPersonaDAL()
        self.mode_service = InteractionModeDAL()

    async def get_chat_history(self, session_id: str, db_session: AsyncSession) -> list[ChatMessage]:
        result = await db_session.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()

    async def create_chat_message(self, message_data: ChatMessageCreate, db_session: AsyncSession) -> dict:
        # Get the session, persona, and mode using existing DAL services
        session = await self.session_service.get_session_by_id(str(message_data.session_id), db_session)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        persona = await self.persona_service.get_ai_persona_by_id(str(message_data.persona_id), db_session)
        if not persona:
            raise HTTPException(status_code=404, detail="AI Persona not found")

        mode = await self.mode_service.get_mode_by_id(str(session.mode_id), db_session)
        if not mode:
            raise HTTPException(status_code=404, detail="Interaction mode not found")

        # Store the user message in the database
        user_message = ChatMessage(
            session_id=message_data.session_id,
            persona_id=message_data.persona_id,
            content=message_data.content,
            role="user"
        )
        db_session.add(user_message)
        await db_session.flush()

        # Get chat history for context
        chat_history = await self.get_chat_history(session.session_id, db_session)
        
        # Format chat history
        formatted_history = ""
        for msg in chat_history:
            if msg.role == "user":
                formatted_history += f"Human: {msg.content}\n"
            else:
                formatted_history += f"AI: {msg.content}\n"

        # Get industry details
        industry_key = persona.industry.lower().replace(" & ", "_and_").replace(" ", "_")
        industry_details = INDUSTRY_DETAILS.get(industry_key, "")

        # Get role details
        role_key = persona.role.lower().replace(" ", "_")
        role_details = ROLE_DETAILS.get(role_key, "")

        # Get experience level details
        experience_key = persona.experience_level.lower()
        experience_details = EXPERIENCE_LEVEL_DETAILS.get(experience_key, "")

        # Get manufacturing model details
        manufacturing_key = persona.manufacturing_model.lower().replace("-", "_")
        manufacturing_details = MANUFACTURING_MODEL_DETAILS.get(manufacturing_key, "")

        # Get geography details
        geography_key = persona.geography.lower().replace(" ", "_")
        geography_details = GEOGRAPHY_DETAILS.get(geography_key, "")

        # Prepare persona context with all required variables
        persona_context = {
            "behavioral_traits": json.dumps(persona.behavioral_traits) if persona.behavioral_traits else "{}",
            "experience_level": persona.experience_level or "",
            "experience_level_details": experience_details,
            "geography": persona.geography or "",
            "geography_details": geography_details,
            "industry": persona.industry or "",
            "industry_details": industry_details,
            "manufacturing_model": persona.manufacturing_model or "",
            "manufacturing_model_details": manufacturing_details,
            "plant_size_impact": persona.plant_size_impact or "",
            "role": persona.role or "",
            "role_details": role_details
        }

        # Create prompt template using the mode's template
        prompt_template = PromptTemplate(
            input_variables=["history", "input"] + list(persona_context.keys()),
            template=mode.prompt_template
        )

        try:
            # Format the prompt with all variables
            formatted_prompt = prompt_template.format(
                history=formatted_history,
                input=message_data.content,
                **persona_context
            )
            
            # Print the complete prompt for debugging
            print("\n[DEBUG] Complete Prompt Template:")
            print("=" * 80)
            print(formatted_prompt)
            print("=" * 80)
            
            # Get AI response directly from LLM
            messages = [
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": message_data.content}
            ]
            response = self.llm.invoke(messages)
            response_content = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"[DEBUG] Error in LLM invoke: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(e)}"
            )

        # Store the AI response in the database
        ai_message = ChatMessage(
            session_id=message_data.session_id,
            persona_id=message_data.persona_id,
            content=response_content,
            role="assistant"
        )
        db_session.add(ai_message)
        await db_session.commit()

        # Get the current timestamp from the database
        result = await db_session.execute(text("SELECT NOW()"))
        current_timestamp = result.scalar()

        # Create response message
        response_message = {
            "message_id": ai_message.message_id,
            "content": response_content,
            "role": "assistant",
            "session_id": message_data.session_id,
            "persona_id": message_data.persona_id,
            "created_at": current_timestamp
        }

        return response_message

    async def process_chat_request(self, chat_request: ChatRequest, db_session: AsyncSession) -> ChatResponse:
        # Create user message
        user_message = ChatMessageCreate(
            content=chat_request.message,
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            role="user"
        )

        # Get AI response
        response_message = await self.create_chat_message(user_message, db_session)

        # Create and return chat response
        return ChatResponse(
            response=response_message["content"],
            session_id=chat_request.session_id,
            persona_id=chat_request.persona_id,
            created_at=response_message["created_at"]
        )
