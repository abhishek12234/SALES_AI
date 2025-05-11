from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from enum import Enum
from typing import Optional

class PlanTypeEnum(str, Enum):
    free_trial = "free_trial"
    single_session = "single_session"
    subscription = "subscription"
    enterprise = "enterprise"

class SubscriptionBase(BaseModel):
    plan_type: PlanTypeEnum
    start_date: date
    end_date: date

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    plan_type: Optional[PlanTypeEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status_active: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    subscription_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }