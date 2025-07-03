from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional

class SessionStatusEnum(str, Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"

class SessionBase(BaseModel):
   
    persona_id: str
    mode_id: Optional[str]= None


class SessionCreate(SessionBase):
    persona_id: str
    mode_id: str

class SessionUpdate(BaseModel):
    persona_id: Optional[str] = None
    mode_id: Optional[str] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    status: Optional[SessionStatusEnum] = None

class SessionResponse(SessionBase):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None 
    performance_report: Optional[dict] = None
    status: SessionStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class PersonaData(BaseModel):
    name: str
    industry: str
    role: str
    experience_level: str
    plant_size_impact: str
    geography: str
    manufacturing_model: str
    