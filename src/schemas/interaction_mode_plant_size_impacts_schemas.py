from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionModePlantSizeImpactBase(BaseModel):
    mode_id: str
    plant_size_impact_id: str
    prompt_template: str

class InteractionModePlantSizeImpactResponse(InteractionModePlantSizeImpactBase):
    interaction_mode_plant_size_impact_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 