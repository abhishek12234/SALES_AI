from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ManufacturingModelBase(BaseModel):
    name: str
    description: str

class ManufacturingModelCreate(ManufacturingModelBase):
    pass

class ManufacturingModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ManufacturingModelResponse(ManufacturingModelBase):
    manufacturing_model_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 