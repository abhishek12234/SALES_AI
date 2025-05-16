from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey, text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    message_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('sessions.session_id'), nullable=False)
    persona_id = Column(String(36), ForeignKey('ai_personas.persona_id'), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(10), nullable=False)  # 'user' or 'assistant'
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # Relationships
    session = relationship("Session", back_populates="messages")
    persona = relationship("AIPersona", back_populates="messages") 