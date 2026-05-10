from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, nullable=False)
    #NOTE:Temporary to make it work cos i don't know where students refrance group(dead code)
    students = relationship("Student", back_populates="group")