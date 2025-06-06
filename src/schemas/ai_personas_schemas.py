from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum
from .industries_schemas import IndustryResponse
from .plant_size_impacts_schemas import PlantSizeImpactResponse
from .manufacturing_models_schemas import ManufacturingModelResponse
from .ai_roles_schemas import AIRoleResponse

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
    behavioral_detail:str

class AIPersonaCreate(AIPersonaBase):
    pass

class AIPersonaUpdate(BaseModel):
    name: Optional[str] = None
    industry_id: Optional[str] = None
    ai_role_id: Optional[str] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    geography: Optional[str] = None
    plant_size_impact_id: Optional[str] = None
    manufacturing_model_id: Optional[str] = None
    behavioral_detail:str 
    status_active: Optional[bool] = None

class IndustrySlim(BaseModel):
    name: str
    industry_id:str


class AIRoleSlim(BaseModel):
    name: str
    ai_role_id:str

class PlantSizeImpactSlim(BaseModel):
    name: str
    plant_size_impact_id: str

class ManufacturingModelSlim(BaseModel):
    name: str
    manufacturing_model_id:str

class AIPersonaResponse(BaseModel):
    persona_id: str
    name: str
    industry: IndustrySlim
    ai_role: AIRoleSlim
    experience_level: ExperienceLevelEnum
    geography: Optional[str] = None
    plant_size_impact: PlantSizeImpactSlim
    manufacturing_model: ManufacturingModelSlim
    status_active: bool

    model_config = {
        "from_attributes": True
    }