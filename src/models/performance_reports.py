from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text, Text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class PerformanceReport(Base):
    __tablename__ = 'performance_reports'

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    session_id = Column(String(36), ForeignKey('sessions.session_id'), nullable=False)
    overall_score = Column(Integer, nullable=True)
    engagement_level = Column(Integer, nullable=True)
    communication_level = Column(Integer, nullable=True)
    objection_handling = Column(Integer, nullable=True)
    adaptability = Column(Integer, nullable=True)
    persuasiveness = Column(Integer, nullable=True)
    create_interest = Column(Integer, nullable=True)
    sale_closing = Column(Integer, nullable=True)
    discovery = Column(Integer, nullable=True)
    cross_selling = Column(Integer, nullable=True)
    solution_fit = Column(Integer, nullable=True)
    coaching_summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    # Relationships
    session = relationship("Session", back_populates="performance_reports")
