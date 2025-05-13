from sqlalchemy import Column, String, TIMESTAMP, Enum, Date, ForeignKey, Boolean,Interval,Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database import Base
import uuid
from sqlalchemy.sql import func 
from sqlalchemy import text

class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    plan_type = Column(
        Enum('free_trial', 'single_session', 'subscription', 'enterprise', name='plan_type_enum'),
        nullable=False
    )
    billing_cycle = Column(
        Enum('monthly', 'yearly', name='billing_cycle_enum'),
        nullable=False,
        server_default=text("'monthly'")
    )

    max_session_duration = Column(Integer, nullable=True)
    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    persona_limit = Column(Integer, nullable=False)
    is_custom = Column(Boolean, nullable=False, server_default=text('false'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"), onupdate=text("now()"))
    # Relationships
 
    payments = relationship("Payment", back_populates="subscription")
    user_subscriptions = relationship("UserSubscription", back_populates="subscription")
