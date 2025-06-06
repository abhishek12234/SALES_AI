from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AIRoleBase(BaseModel):
    name: str
    description: str

class AIRoleCreate(AIRoleBase):
    pass

class AIRoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AIRoleResponse(AIRoleBase):
    ai_role_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 