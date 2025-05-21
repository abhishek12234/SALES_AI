from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionModeManufacturingModelBase(BaseModel):
    mode_id: str
    manufacturing_model: str
    prompt_template: str

class InteractionModeManufacturingModelResponse(InteractionModeManufacturingModelBase):
    interaction_mode_manufacturing_model_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 