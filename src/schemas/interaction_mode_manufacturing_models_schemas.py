from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.interaction_modes_schemas import InteractionModeResponse
from schemas.manufacturing_models_schemas import ManufacturingModelResponse
class InteractionModeManufacturingModelBase(BaseModel):
    mode_id: str
    manufacturing_model_id: str
    prompt_template: str

class InteractionModeManufacturingModelResponse(BaseModel):
    interaction_mode_manufacturing_model_id: str
    interaction_mode: InteractionModeResponse
    manufacturing_model: ManufacturingModelResponse
    prompt_template: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 