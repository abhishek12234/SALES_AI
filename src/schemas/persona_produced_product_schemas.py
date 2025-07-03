from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductSlim(BaseModel):
    name: str
    details: str
    product_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class PersonaProducedProductBase(BaseModel):
    persona_id: str
    product_id: str

class PersonaProducedProductCreate(PersonaProducedProductBase):
    pass

class PersonaProducedProductUpdate(BaseModel):
    persona_id: Optional[str] = None
    product_id: Optional[str] = None

class PersonaProducedProductResponse(BaseModel):
    persona_product_id: str
    product: Optional[ProductSlim] = None

    model_config = {
        "from_attributes": True
    } 