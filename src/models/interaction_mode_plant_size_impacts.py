from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class InteractionModePlantSizeImpact(Base):
    __tablename__ = 'interaction_mode_plant_size_impacts'
    __table_args__ = (
        UniqueConstraint('mode_id', 'plant_size_impact_id', name='uq_mode_plant_size_impact'),
    )

    interaction_mode_plant_size_impact_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mode_id = Column(String(36), ForeignKey('interaction_modes.mode_id'), nullable=False)
    plant_size_impact_id = Column(String(36), ForeignKey('plant_size_impacts.plant_size_impact_id'), nullable=False)
    prompt_template = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 