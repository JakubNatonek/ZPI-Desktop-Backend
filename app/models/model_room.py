from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.model_activity import room_activities
from app.models.model_room_department import room_departments
from app.models.model_special_equipment import room_special_equipment


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    number = Column(String, nullable=False)
    seats = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    type_id = Column(Integer, ForeignKey("room_type.id"), nullable=True)

    room_type = relationship("RoomType")
    departments = relationship("Department", secondary=room_departments, back_populates="rooms")
    activities = relationship("Activity", secondary=room_activities, back_populates="rooms")
    special_equipment = relationship("SpecialEquipment", secondary=room_special_equipment, back_populates="rooms")