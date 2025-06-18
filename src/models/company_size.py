from sqlalchemy import Column, String, TIMESTAMP, text, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class CompanySize(Base):
    __tablename__ = 'company_size'

    company_size_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # relationship
    ai_persona = relationship("AIPersona", back_populates="company_size_new") 