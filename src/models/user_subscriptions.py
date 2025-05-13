from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean, Interval, Integer, Time
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from database import Base
import uuid
from sqlalchemy.sql import text

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    user_subscription_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)
    subscription_id = Column(String(36), ForeignKey('subscriptions.subscription_id'), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)
    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    time_used = Column(Integer, nullable=False, server_default=text('0'))  # or Integer for seconds
    sessions_completed = Column(Integer, nullable=False, server_default=text('0'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"), onupdate=text("now()"))

    user = relationship("User", back_populates="user_subscriptions")
    subscription = relationship("Subscription", back_populates="user_subscriptions", lazy="selectin") 