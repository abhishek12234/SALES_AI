from sqlalchemy import Column, String, UUID, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from database import Base
import uuid
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy import text

class RolePermission(Base):
    __tablename__ = 'role_permissions'

    permission_id =  Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    role_id = Column(String(36), ForeignKey('roles.role_id'), nullable=False)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
        # Relationships
    role = relationship("Role", back_populates="permissions")