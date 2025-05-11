from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RolePermissionBase(BaseModel):
    resource: str
    action: str

class RolePermissionCreate(RolePermissionBase):
    role_id: str

class RolePermissionUpdate(BaseModel):
    resource: Optional[str] = None
    action: Optional[str] = None

class RolePermissionResponse(RolePermissionBase):
    permission_id: str
    role_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }