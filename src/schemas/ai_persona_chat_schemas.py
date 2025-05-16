from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str
    role: str  # 'user' or 'assistant'

class ChatMessageCreate(BaseModel):
    content: str
    session_id: UUID4
    persona_id: UUID4
    role: Optional[str] = "user"  # Make optional with default

class ChatMessageResponse(ChatMessageBase):
    message_id: str
    session_id: str
    persona_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    session_id: str
    persona_id: str
    user_id: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse]

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: UUID4
    persona_id: UUID4

class ChatResponse(BaseModel):
    response: str
    session_id: UUID4
    persona_id: UUID4
    created_at: datetime
