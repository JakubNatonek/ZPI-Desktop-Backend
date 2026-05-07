from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class TeachingLoadAssignment(Base):
    __tablename__ = "teaching_load_assignments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True)
    hours = Column(Integer, nullable=False)

    teacher = relationship("User", back_populates="teaching_load_assignments", foreign_keys=[teacher_id])
    subject = relationship("Subject")
    activity = relationship("Activity")
    semester = relationship("Semestr")
