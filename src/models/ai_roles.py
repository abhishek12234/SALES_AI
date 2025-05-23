from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class AIRole(Base):
    __tablename__ = 'ai_roles'

    ai_role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 

    #relationships
    ai_persona = relationship("AIPersona", back_populates="ai_role")