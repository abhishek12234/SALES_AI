from sqlalchemy import Column, String, TIMESTAMP, Text, Enum, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
from database import Base
import uuid

class AIPersona(Base):
    __tablename__ = 'ai_personas'

    persona_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    industry = Column(String(100), nullable=True)
    role = Column(Enum('quality_manager', 'production_manager', 'maintenance_manager', 'plant_manager', name='role_enum'), nullable=True)
    experience_level = Column(Enum('junior', 'mid', 'senior', name='experience_level_enum'), nullable=True)
    geography = Column(Text, nullable=True)
    
    manufacturing_model = Column(Enum('self_manufacturing', 'contract_manufacturing', name='manufacturing_model_enum'), nullable=True)
    behavioral_traits = Column(JSON, nullable=True)

    plant_size_impact = Column(Enum(
        'small', 'medium', 'large',
        name='plant_size_impact_enum'
    ), nullable=True, comment="Plant Size Impact: small (<50 employees): Cash flow sensitivity, resource constraints, downtime impact, expedited decisions; medium (50-200): Balanced cost/capability concerns, department approvals, scalability focus; large (>200): Complex approval process, enterprise standards, formal documentation, corporate alignment")

    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    # Relationships
    sessions = relationship("Session", back_populates="persona")
