from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanySizeBase(BaseModel):
    name: str
    description: str

class CompanySizeCreate(CompanySizeBase):
    pass

class CompanySizeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CompanySizeResponse(CompanySizeBase):
    company_size_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 