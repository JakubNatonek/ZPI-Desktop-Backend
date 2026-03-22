from sqlalchemy import Boolean, Column, Integer, String

from app.core.database import Base


class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    rodzaj = Column(String, nullable=False)
    rodzajshow = Column(String, nullable=True)
    prop_sal = Column(String, nullable=True)
    zablokowany = Column(Boolean, nullable=False, default=False)
    periodyczny = Column(Boolean, nullable=False, default=False)