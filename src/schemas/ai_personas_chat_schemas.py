from pydantic import BaseModel
from enum import Enum



class ManufacturingModelEnum(str, Enum):
    self_manufacturing = "self_manufacturing"
    contract_manufacturing = "contract_manufacturing"

class ExperienceLevelEnum(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"

class PlantSizeImpactEnum(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class RoleEnum(str, Enum):
    quality_manager = "quality_manager"
    production_manager = "production_manager"
    maintenance_manager = "maintenance_manager"
    plant_manager = "plant_manager"

class ChatWithPersonaRequest(BaseModel):
    persona_id: str
    industry: str
    manufacturing_model: ManufacturingModelEnum
    role: RoleEnum
    user_input: str
    geography: str
    plant_size_impact: PlantSizeImpactEnum