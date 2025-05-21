from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IndustryBase(BaseModel):
    name: str

class IndustryCreate(IndustryBase):
    pass

class IndustryUpdate(BaseModel):
    name: Optional[str] = None

class IndustryResponse(IndustryBase):
    industry_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 