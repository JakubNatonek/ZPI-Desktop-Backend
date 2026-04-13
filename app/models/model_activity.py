from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.core.database import Base


room_activities = Table(
    "room_activities",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("room.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), unique=True, nullable=False)

    rooms = relationship("Room", secondary=room_activities, back_populates="activities")
    subject_activities = relationship("SubjectActivity", back_populates="activity")