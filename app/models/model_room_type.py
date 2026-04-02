from sqlalchemy import Column, Integer, String

from app.core.database import Base


class RoomType(Base):
    __tablename__ = "room_type"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=False)