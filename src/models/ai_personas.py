from sqlalchemy import Column, String, TIMESTAMP, Text, Enum, text, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
from database import Base
import uuid

class AIPersona(Base):
    __tablename__ = 'ai_personas'
    __table_args__ = (

        UniqueConstraint(
            'name',
            'industry_id',
            'ai_role_id',
            'experience_level',
            'geography',
            'plant_size_impact_id',
            'manufacturing_model_id',
            name='uq_ai_persona_unique_combo'
        ),
    )

    persona_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(100), nullable=False)
    industry_id = Column(String(36), ForeignKey('industries.industry_id'), nullable=False)
    ai_role_id = Column(String(36), ForeignKey('ai_roles.ai_role_id'), nullable=False)
    experience_level = Column(Enum("junior", "mid", "senior"), nullable=False)
    geography = Column(Text, nullable=False)
    plant_size_impact_id = Column(String(36), ForeignKey('plant_size_impacts.plant_size_impact_id'), nullable=False)
    manufacturing_model_id = Column(String(36), ForeignKey('manufacturing_models.manufacturing_model_id'), nullable=False)
    behavioral_detail = Column(Text, nullable=False)
    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # Relationships
    industry = relationship("Industry", back_populates="ai_persona",lazy="selectin")
    ai_role = relationship("AIRole",back_populates="ai_persona",lazy="selectin")
    plant_size_impact = relationship("PlantSizeImpact",back_populates="ai_persona",lazy="selectin")
    manufacturing_model = relationship("ManufacturingModel",back_populates="ai_persona",lazy="selectin")
    sessions=relationship("Session", back_populates="persona")













    