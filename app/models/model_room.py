from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.model_activity import room_activities
from app.models.model_room_type import RoomType


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    building = Column(String, nullable=False) # NOTE: To seprate table bind with departments
    number = Column(String, nullable=False)
    seats = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    type_id = Column(Integer, ForeignKey("room_type.id"), nullable=True)

    type = relationship("RoomType")
    activities = relationship("Activity", secondary=room_activities, back_populates="rooms")