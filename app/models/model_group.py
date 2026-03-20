from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spec = Column(String, nullable=False)
    kod = Column(String, nullable=False)
    rok = Column(Integer, nullable=False)
    studia = Column(String, nullable=False)

    students = relationship("Student", back_populates="group")