from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ManufacturingModelEnum(str, Enum):
    self_manufacturing = "self_manufacturing"
    contract_manufacturing = "contract_manufacturing"

class ExperienceLevelEnum(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"

class RoleEnum(str, Enum):
    quality_manager = "quality_manager"
    production_manager = "production_manager"
    maintenance_manager = "maintenance_manager"
    plant_manager = "plant_manager"

class PlantSizeImpactEnum(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class AIPersonaBase(BaseModel):
    name: str
    industry: Optional[str] = None
    role: Optional[RoleEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    plant_size_impact: Optional[PlantSizeImpactEnum] = None
    geography: Optional[str] = None
    manufacturing_model: Optional[ManufacturingModelEnum] = None
    behavioral_traits: Optional[list] = None  # List of dicts: {name, intensity, description}


class AIPersonaCreate(AIPersonaBase):
    pass

class AIPersonaUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    role: Optional[RoleEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    geography: Optional[str] = None
    manufacturing_model: Optional[ManufacturingModelEnum] = None
    behavioral_traits: Optional[list] = None
    status_active: Optional[bool] = None
    plant_size_impact: Optional[PlantSizeImpactEnum] = None
   

class AIPersonaResponse(AIPersonaBase):
    persona_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime
 

    model_config = {
        "from_attributes": True
    }