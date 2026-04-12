from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.core.database import Base


room_special_equipment = Table(
    "room_special_equipment",
    Base.metadata,
    Column("room_id", Integer, ForeignKey("room.id"), primary_key=True),
    Column("special_equipment_id", Integer, ForeignKey("special_equipment.id"), primary_key=True),
)


class SpecialEquipment(Base):
    __tablename__ = "special_equipment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), unique=True, nullable=False)

    rooms = relationship("Room", secondary=room_special_equipment, back_populates="special_equipment")