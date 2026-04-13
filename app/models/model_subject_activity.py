from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubjectActivity(Base):
    __tablename__ = "subject_activities"
    __table_args__ = (
        UniqueConstraint("subject_id", "activity_id", name="uq_subject_activities_subject_activity"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)

    subject = relationship("Subject", back_populates="subject_activities", foreign_keys=[subject_id])
    activity = relationship("Activity", back_populates="subject_activities")
