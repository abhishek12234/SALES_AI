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
    user_id: str
    persona_id: str
    mode_id: str


class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    persona_id: Optional[str] = None
    mode_id: Optional[str] = None
    end_time: Optional[datetime] = None
    duration: Optional[str] = None
    status: Optional[SessionStatusEnum] = None

class SessionResponse(SessionBase):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[str] = None  # interval as string
    status: SessionStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }