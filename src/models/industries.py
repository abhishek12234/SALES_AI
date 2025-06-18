from sqlalchemy import Column, String, TIMESTAMP, text, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Industry(Base):
    __tablename__ = 'industries'

    industry_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    details = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 

    #relationships
    ai_persona = relationship("AIPersona", back_populates="industry")
    produced_product_categories = relationship("ProducedProductCategory", back_populates="industry")