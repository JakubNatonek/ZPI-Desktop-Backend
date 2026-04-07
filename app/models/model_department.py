from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Department(Base):

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    abbreviation = Column(String, unique=True, nullable=False)