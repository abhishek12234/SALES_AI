from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid

class PersonaProducedProduct(Base):
    __tablename__ = 'persona_produced_product'

    persona_product_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    persona_id = Column(String(36), ForeignKey('ai_personas.persona_id'), nullable=False)
    product_id = Column(String(36), ForeignKey('produced_product_category.product_id'), nullable=False)

    # Relationships
    ai_persona = relationship('AIPersona', back_populates='persona_products')
    product = relationship('ProducedProductCategory', back_populates='persona_products', lazy='selectin')
     