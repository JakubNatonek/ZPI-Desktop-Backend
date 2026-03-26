from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RaplaDataType(Base):
    __tablename__ = "rapla_data_type"

    # Internal data
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Rapla data
    type = Column(String(255))