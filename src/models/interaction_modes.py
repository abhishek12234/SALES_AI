from sqlalchemy import Column, String, TIMESTAMP, Text, text, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
import uuid

class InteractionMode(Base):
    __tablename__ = 'interaction_modes'

    mode_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Enum('prospecting', 'discovering', 'closing', name='interaction_mode_enum'), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    prompt_template = Column(Text, nullable=False)
    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    # Relationships
    sessions = relationship("Session", back_populates="mode")
    interaction_manufacturing_models = relationship("InteractionModeManufacturingModel", back_populates="interaction_mode")
