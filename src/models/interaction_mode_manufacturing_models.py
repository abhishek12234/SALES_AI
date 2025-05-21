from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, UniqueConstraint, Text
from database import Base
import uuid

class InteractionModeManufacturingModel(Base):
    __tablename__ = 'interaction_mode_manufacturing_models'
    __table_args__ = (
        UniqueConstraint('mode_id', 'manufacturing_model_id', name='uq_mode_manufacturing_model'),
    )

    interaction_mode_manufacturing_model_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mode_id = Column(String(36), ForeignKey('interaction_modes.mode_id'), nullable=False)
    manufacturing_model_id = Column(String(36), ForeignKey('manufacturing_models.manufacturing_model_id'), nullable=False)
    prompt_template = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 