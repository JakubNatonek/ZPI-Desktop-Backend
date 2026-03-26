from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RaplaOptionalElement(Base):
   __tablename__ = "rapla_optional_element"

   # Internal data
   id = Column(Integer, primary_key=True, index=True, autoincrement=True)

   # Rapla data
   name = Column(String(255), nullable=False)
   default_value = Column(String, nullable=True)
