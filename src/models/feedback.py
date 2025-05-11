from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Feedback(Base):
    __tablename__ = 'feedback'

    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    session_id = Column(String(36), ForeignKey('sessions.session_id'), nullable=False)
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    # Relationships
    user = relationship("User", back_populates="feedback")
    session = relationship("Session", back_populates="feedback")
