from typing import Any, Dict, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entity_name = Column(String, nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    action = Column(String, nullable=False) # CREATE, UPDATE, DELETE
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    modified_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User")
