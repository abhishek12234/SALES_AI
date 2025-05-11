from sqlalchemy import Column, String, TIMESTAMP, Enum, Date, ForeignKey, Boolean
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
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"), onupdate=text("now()"))
    # Relationships
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")
