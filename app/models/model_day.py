from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Day(Base):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(16), nullable=False, unique=True)
