from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlantSizeImpactBase(BaseModel):
    name: str
    description: str

class PlantSizeImpactCreate(PlantSizeImpactBase):
    pass

class PlantSizeImpactUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PlantSizeImpactResponse(PlantSizeImpactBase):
    plant_size_impact_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 