from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.model_room_department import room_departments

class Department(Base):

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    name = Column(String, unique=True, nullable=False)
    abbreviation = Column(String, unique=True, nullable=False)

    rooms = relationship("Room", secondary=room_departments, back_populates="departments")