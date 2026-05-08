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
    hours = Column(Integer, nullable=False, default=0)

    teacher = relationship("User", foreign_keys=[teacher_id])
    subject = relationship("Subject", foreign_keys=[subject_id])
    activity = relationship("Activity", foreign_keys=[activity_id])
    semester = relationship("Semestr", foreign_keys=[semester_id])

    def __repr__(self) -> str:
        return f"<TeachingLoadAssignment(id={self.id}, teacher_id={self.teacher_id}, hours={self.hours})>"
