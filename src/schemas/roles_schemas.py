from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    sales_person = "sales_person"
    manager = "manager"
    admin = "admin"
    super_admin = "super_admin"

class RoleBase(BaseModel):
    name: RoleEnum
    description: Optional[str] = None

 

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[RoleEnum] = None
    description: Optional[str] = None
    status_active: Optional[bool] = None

class RoleResponse(RoleBase):
    role_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
