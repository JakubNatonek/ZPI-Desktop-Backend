from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class RaplaCategory(Base):
   __tablename__ = "rapla_category"

   # Internal data
   id = Column(Integer, primary_key=True, index=True, autoincrement=True)

   # Rapla data
   uuid = Column(String(100), nullable=False, unique=True)
   created_at = Column(DateTime(timezone=True), nullable=True)
   last_changed = Column(DateTime(timezone=True), nullable=True)
   key = Column(String(255), nullable=False)
   parent_id = Column(Integer, ForeignKey("rapla_category.id"), nullable=True)