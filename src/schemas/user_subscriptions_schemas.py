from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional
from schemas.subscriptions_schemas import SubscriptionResponse

class UserSubscriptionBase(BaseModel):
    user_id: str
    subscription_id: str
 

class UserSubscriptionCreate(UserSubscriptionBase):
    pass

class UserSubscriptionUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status_active: Optional[bool] = None
    time_used: Optional[int] = None
    sessions_completed: Optional[int] = None

class UserSubscriptionResponse(BaseModel):
    user_subscription_id: str
    subscription: SubscriptionResponse
    status_active: bool = True
    start_date: datetime
    end_date: datetime
    time_used: Optional[int] = None
    sessions_completed: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    } 