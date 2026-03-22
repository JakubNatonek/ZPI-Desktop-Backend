from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    specialization = Column(String, nullable=False)
    code = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    studies_type = Column(String, nullable=False)

    students = relationship("Student", back_populates="group")