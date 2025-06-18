from sqlalchemy import Column, String, TIMESTAMP, text, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid

class ProducedProductCategory(Base):
    __tablename__ = 'produced_product_category'

    product_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    industry_id = Column(String(36), ForeignKey('industries.industry_id'), nullable=False)
    name = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))

    # relationship
    industry = relationship("Industry", back_populates="produced_product_categories")
