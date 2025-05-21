from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionModeAIRoleBase(BaseModel):
    mode_id: str
    ai_role: str
    prompt_template: str

class InteractionModeAIRoleResponse(InteractionModeAIRoleBase):
    interaction_mode_ai_role_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True 