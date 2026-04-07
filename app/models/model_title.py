from sqlalchemy import Column, Integer, String

from app.core.database import Base


class TitleModel(Base):

    __tablename__ = "title"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
