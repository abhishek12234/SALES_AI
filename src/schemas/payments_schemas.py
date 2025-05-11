from pydantic import BaseModel, condecimal
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentStatusEnum(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"
    failed = "failed"
    refunded = "refunded"

class PaymentBase(BaseModel):
    subscription_id: str
    user_id: str
    amount: condecimal(max_digits=10, decimal_places=2)
    currency: str
    payment_status: PaymentStatusEnum
    payment_method: str
    payment_date: datetime

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    currency: Optional[str] = None
    payment_status: Optional[PaymentStatusEnum] = None
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    payment_id: str
    created_at: datetime
    updated_at: datetime
    # Optionally, include nested user and subscription info
    # user: Optional[UserResponse]
    # subscription: Optional[SubscriptionResponse]

    model_config = {
        "from_attributes": True
    } 