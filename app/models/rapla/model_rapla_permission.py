from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RaplaPermission(Base):
    __tablename__ = "rapla_permission"
    # Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Rapla data
    access = Column(String(255))
    group = Column(String(255), nullable=True)