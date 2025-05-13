from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional

class PlanTypeEnum(str, Enum):
    free_trial = "free_trial"
    single_session = "single_session"
    subscription = "subscription"
    enterprise = "enterprise"

class BillingCycleEnum(str, Enum):
    monthly = "monthly"
    yearly = "yearly"

class SubscriptionBase(BaseModel):
    plan_type: PlanTypeEnum
    billing_cycle: BillingCycleEnum

    max_session_duration:int
    persona_limit: int
    is_custom: bool = False

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    plan_type: Optional[PlanTypeEnum] = None
    billing_cycle: Optional[BillingCycleEnum] = None
    status_active: Optional[bool] = None
    max_session_duration:int
    persona_limit: Optional[int] = None
    is_custom: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    subscription_id: str
    status_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }