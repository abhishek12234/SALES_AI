from sqlalchemy import Column, String, TIMESTAMP, Text
from database import Base
import uuid
from sqlalchemy.sql import text

class CoachingSummary(Base):
    __tablename__ = 'coaching_summary'

    coaching_summary_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
