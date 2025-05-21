from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlantSizeImpactBase(BaseModel):
    name: str

class PlantSizeImpactResponse(PlantSizeImpactBase):
    plant_size_impact_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 