from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class RaplaDefineElement(Base):
   __tablename__ = "rapla_define_element"

   # Internal data
   id = Column(Integer, primary_key=True, index=True, autoincrement=True)

   # Rapla data
   name = Column(String(255),unique=True, index=True, nullable=False)
   uuid = Column(String(100), nullable=False, index=True, unique=True)
   created_at = Column(DateTime(timezone=True), nullable=True)
   last_changed = Column(DateTime(timezone=True), nullable=True)
   last_changed_by = Column(String(255), nullable=False)