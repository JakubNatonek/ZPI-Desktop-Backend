from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    index_number = Column(String, unique=True, nullable=True, index=True)
    group_id = Column(Integer, ForeignKey("group.id", ondelete="SET NULL"), nullable=True, index=True)
    semester = Column(Integer, nullable=True)

    user = relationship("User", back_populates="student_profile")
    group = relationship("Group", back_populates="students")
