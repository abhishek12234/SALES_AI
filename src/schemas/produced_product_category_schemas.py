from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProducedProductCategoryBase(BaseModel):
    industry_id: str
    name: str
    details: str

class ProducedProductCategoryCreate(ProducedProductCategoryBase):
    pass

class ProducedProductCategoryUpdate(BaseModel):
    industry_id: Optional[str] = None
    name: Optional[str] = None
    details: Optional[str] = None

class ProducedProductCategoryResponse(ProducedProductCategoryBase):
    product_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
