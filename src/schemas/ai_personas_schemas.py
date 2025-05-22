from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class ExperienceLevelEnum(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"

class AIPersonaBase(BaseModel):
    name: str
    industry_id: str
    ai_role_id: str
    experience_level: ExperienceLevelEnum
    geography: Optional[str] = None
    plant_size_impact_id: str
    manufacturing_model_id: str
    behavioral_traits: Optional[List[Dict]] = None

class AIPersonaCreate(AIPersonaBase):
    pass

class AIPersonaUpdate(BaseModel):
    name: Optional[str] = None
    industry_id: Optional[str] = None
    ai_role_id: Optional[str] = None
    experience_level: Optional[str] = None
    geography: Optional[str] = None
    plant_size_impact_id: Optional[str] = None
    manufacturing_model_id: Optional[str] = None
    behavioral_traits: Optional[List[Dict]] = None
    status_active: Optional[bool] = None

class AIPersonaResponse(AIPersonaBase):
    persona_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }