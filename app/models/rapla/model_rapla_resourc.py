
from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base

class ModelRaplaResourc(Base):
    __tablename__ = "rapla_resourc"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    uuid = Column(String(100), nullable=False, index=True, unique=True)
    owner = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    last_changed = Column(DateTime(timezone=True), nullable=True)
    last_changed_by = Column(String(100), nullable=False)