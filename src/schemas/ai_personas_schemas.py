from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum
from .industries_schemas import IndustryResponse
from .plant_size_impacts_schemas import PlantSizeImpactResponse
from .manufacturing_models_schemas import ManufacturingModelResponse
from .ai_roles_schemas import AIRoleResponse
from .persona_produced_product_schemas import PersonaProducedProductResponse

# class ExperienceLevelEnum(str, Enum):
#     junior = "junior"
#     mid = "mid"
#     senior = "senior"

class AIPersonaBase(BaseModel):
    name: str
    industry_id: str
    ai_role_id: str
    #experience_level: ExperienceLevelEnum
    geography: Optional[str] = None
    plant_size_impact_id: str
    manufacturing_model_id: str
    behavioral_detail: str
    company_size_id: str
    profile_pic: Optional[str] = None  # Path or identifier for the uploaded profile picture

class AIPersonaCreate(AIPersonaBase):
    pass

class AIPersonaUpdate(BaseModel):
    name: Optional[str] = None
    industry_id: Optional[str] = None
    ai_role_id: Optional[str] = None
    #experience_level: Optional[ExperienceLevelEnum] = None
    geography: Optional[str] = None
    company_size_id: Optional[str] = None
    plant_size_impact_id: Optional[str] = None
    manufacturing_model_id: Optional[str] = None
    behavioral_detail: Optional[str] = None
    profile_pic: Optional[str] = None  # Path or identifier for the uploaded profile picture
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

class CompanySizeModelSlim(BaseModel):
    name: str
    company_size_id:str

class AIPersonaResponse(BaseModel):
    persona_id: str
    name: str
    industry: IndustrySlim
    ai_role: AIRoleSlim
    #experience_level: ExperienceLevelEnum
    geography: Optional[str] = None
    plant_size_impact: PlantSizeImpactSlim
    manufacturing_model: ManufacturingModelSlim
    company_size_new: CompanySizeModelSlim
    behavioral_detail: str
    status_active: bool
    profile_pic: Optional[str] = None  # Add this field to include the profile picture path or identifier
    persona_products: List[PersonaProducedProductResponse] = []

    model_config = {
        "from_attributes": True
    }