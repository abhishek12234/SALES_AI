from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# 🧾 Type alias for 0–100 score range
Score100 = int

class PerformanceReportBase(BaseModel):
    session_id: str
    overall_score: Optional[Score100] = None
    engagement_level: Optional[Score100] = None
    communication_level: Optional[Score100] = None
    objection_handling: Optional[Score100] = None
    adaptability: Optional[Score100] = None
    persuasiveness: Optional[Score100] = None
    create_interest: Optional[Score100] = None
    sale_closing: Optional[Score100] = None
    discovery: Optional[Score100] = None
    cross_selling: Optional[Score100] = None
    solution_fit: Optional[Score100] = None
    coaching_summary: Optional[str] = None

class PerformanceReportCreate(PerformanceReportBase):
    pass

class PerformanceReportUpdate(BaseModel):
    overall_score: Optional[Score100] = None
    engagement_level: Optional[Score100] = None
    communication_level: Optional[Score100] = None
    objection_handling: Optional[Score100] = None
    adaptability: Optional[Score100] = None
    persuasiveness: Optional[Score100] = None
    create_interest: Optional[Score100] = None
    sale_closing: Optional[Score100] = None
    discovery: Optional[Score100] = None
    cross_selling: Optional[Score100] = None
    solution_fit: Optional[Score100] = None
    coaching_summary: Optional[str] = None

class PerformanceReportResponse(PerformanceReportBase):
    report_id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
