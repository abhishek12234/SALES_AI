from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class InteractionModeAIRole(Base):
    __tablename__ = 'interaction_mode_ai_roles'
    __table_args__ = (
        UniqueConstraint('mode_id', 'ai_role_id', name='uq_mode_ai_role'),
    )

    interaction_mode_ai_role_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mode_id = Column(String(36), ForeignKey('interaction_modes.mode_id'), nullable=False)
    ai_role_id = Column(String(36), ForeignKey('ai_roles.ai_role_id'), nullable=False)
    prompt_template = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()")) 