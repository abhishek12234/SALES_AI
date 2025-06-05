from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class PlantSizeImpact(Base):
    __tablename__ = 'plant_size_impacts'

    plant_size_impact_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 

    #relationship
    ai_persona = relationship("AIPersona", back_populates="plant_size_impact")
