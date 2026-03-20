from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    building = Column(String, nullable=False)
    number = Column(String, nullable=False)
    seats = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=True)
    activities = Column(Text, nullable=True)