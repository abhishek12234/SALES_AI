from sqlalchemy import Column, String, TIMESTAMP, Enum, ForeignKey, UniqueConstraint, CheckConstraint, text, Boolean
from sqlalchemy.dialects.mysql import VARCHAR, CHAR
from sqlalchemy.orm import relationship
from database import Base
import uuid
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True, default=uuid.uuid4, nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    google_id = Column(VARCHAR(255), nullable=True, unique=True)
    phone_number = Column(VARCHAR(255), nullable=True, unique=True)
    otp_code = Column(VARCHAR(255), nullable=True)
    otp_expiry = Column(TIMESTAMP, nullable=True)
    password_hash = Column(VARCHAR(255), nullable=True)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50), nullable=False)
    role_id = Column(String(36), ForeignKey('roles.role_id'), nullable=True)

    status_active = Column(Boolean, nullable=False, server_default=text('true'))
    is_verified = Column(Boolean, nullable=False, server_default=text('false'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"), onupdate=text("now()"))

    # Relationships
    feedback = relationship("Feedback", back_populates="user")
    role = relationship("Role", back_populates="users", lazy="selectin")
    sessions = relationship("Session", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    user_subscriptions = relationship("UserSubscription", back_populates="user", lazy="selectin", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('google_id', name='uq_user_google_id'),
        UniqueConstraint('phone_number', name='uq_user_phone_number'),
        CheckConstraint("LENGTH(otp_code) = 6 OR otp_code IS NULL", name="check_otp_code_length"),
        CheckConstraint("CHAR_LENGTH(first_name) > 0", name="check_first_name_not_empty"),
        CheckConstraint("CHAR_LENGTH(last_name) > 0", name="check_last_name_not_empty"),
    )
