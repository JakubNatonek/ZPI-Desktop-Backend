from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    budynek = Column(String, nullable=False)
    nr = Column(String, nullable=False)
    miejsca = Column(Integer, nullable=False)
    opis = Column(String, nullable=True)
    typ = Column(String, nullable=True)