from sqlalchemy import Column, String, TIMESTAMP, Enum, Integer, ForeignKey, text
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.mysql import VARCHAR, CHAR
import uuid

from sqlalchemy import Column, String, TIMESTAMP, Enum, Integer, ForeignKey, text

class Session(Base):
    __tablename__ = 'sessions'

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    persona_id = Column(String(36), ForeignKey('ai_personas.persona_id'), nullable=True)
    mode_id = Column(String(36), ForeignKey('interaction_modes.mode_id'), nullable=True)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=True)
    duration = Column(Integer, nullable=False, server_default=text("0"))  # Changed from Integer to String for interval, now with length
    status = Column(Enum('active', 'completed', 'abandoned', name='session_status_enum'), nullable=False, server_default=text("'abandoned'"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # Relationships
    user = relationship("User", back_populates="sessions")
    persona = relationship("AIPersona", back_populates="sessions")
    mode = relationship("InteractionMode", back_populates="sessions")
    feedback = relationship("Feedback", back_populates="session")
    performance_reports = relationship("PerformanceReport", back_populates="session")