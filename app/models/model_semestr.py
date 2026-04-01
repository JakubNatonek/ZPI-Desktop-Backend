from sqlalchemy import Column, Date, Integer, String

from app.core.database import Base


class Semestr(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_rozpoczecia = Column(Date, nullable=False)
    data_zakonczenia = Column(Date, nullable=False)
    nazwa = Column(String(100), nullable=False)
