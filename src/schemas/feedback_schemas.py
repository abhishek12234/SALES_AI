from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    user_id: str
    session_id: str

class FeedbackUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    feedback_id: str
    user_id: str
    session_id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }