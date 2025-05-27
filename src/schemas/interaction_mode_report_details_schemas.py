from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionModeReportDetailBase(BaseModel):
    mode_id: str
    prompt_template: str

class InteractionModeReportDetailResponse(InteractionModeReportDetailBase):
    report_detail_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 