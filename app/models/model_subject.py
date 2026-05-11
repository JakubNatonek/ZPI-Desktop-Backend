from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


# NOTE: What dose this even do.
class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("subject_activities.id"), nullable=True, index=True)
    type_display = Column(String, nullable=True)
    room_properties = Column(String, nullable=True)
    blocked = Column(Boolean, nullable=False, default=False)
    periodic = Column(Boolean, nullable=False, default=False)

    type_link = relationship("SubjectActivity", foreign_keys=[type_id], post_update=True)
    subject_activities = relationship(
        "SubjectActivity",
        back_populates="subject",
        foreign_keys="SubjectActivity.subject_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    field_links = relationship(
        "SubjectForFieldOfStudy",
        back_populates="subject",
        foreign_keys="SubjectForFieldOfStudy.subject_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )