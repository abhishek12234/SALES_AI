from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class InteractionModeNameEnum(str, Enum):
    prospecting = "prospecting"
    discovering = "discovering"
    closing = "closing"

class InteractionModeBase(BaseModel):
    name: InteractionModeNameEnum
    description: Optional[str] = None
    prompt_template: Optional[str] = None

class InteractionModeCreate(InteractionModeBase):
    pass

class InteractionModeUpdate(BaseModel):
    name: Optional[InteractionModeNameEnum] = None
    description: Optional[str] = None
    status_active: Optional[bool] = None
    prompt_template: Optional[str] = None

class InteractionModeResponse(InteractionModeBase):
    mode_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }