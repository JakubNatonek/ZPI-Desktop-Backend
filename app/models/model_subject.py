from sqlalchemy import Boolean, Column, Integer, String

from app.core.database import Base


class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    type_display = Column(String, nullable=True)
    room_properties = Column(String, nullable=True)
    blocked = Column(Boolean, nullable=False, default=False)
    periodic = Column(Boolean, nullable=False, default=False)