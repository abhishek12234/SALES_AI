from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Numeric, Enum, text
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    subscription_id = Column(String(36), ForeignKey('subscriptions.subscription_id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)  # Fixed: Added precision and scale
    currency = Column(String(3), nullable=False)
    payment_status = Column(Enum('pending', 'paid', 'cancelled', 'failed', 'refunded', name='payment_status_enum'), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
