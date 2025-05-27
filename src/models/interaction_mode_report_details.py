from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, Text
from database import Base
import uuid

class InteractionModeReportDetail(Base):
    __tablename__ = 'interaction_mode_report_details'

    report_detail_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    mode_id = Column(String(36), ForeignKey('interaction_modes.mode_id'), nullable=False)
    prompt_template = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # Relationship
    # interaction_mode = relationship("InteractionMode", back_populates="report_details", lazy="selectin") 