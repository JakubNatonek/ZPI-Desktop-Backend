from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class RaplaUser(Base):
    __tablename__ = "rapla_user"

# Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

# Rapla data
    uuid = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    last_changed = Column(DateTime(timezone=True), nullable=True)
    username = Column(String(100))
    password = Column(String(100))
    name = Column(String(255))
    email = Column(String(255))
    isadmin = Column(Boolean)
    # Temporary
    xml_value = Column(Text)
