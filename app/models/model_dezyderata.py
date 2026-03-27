from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dezyderata(Base):
    __tablename__ = "dezyderaty"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    data_od = Column(Date, nullable=False)
    data_do = Column(Date, nullable=False)
    godziny = Column(Text, nullable=False)  # JSON string z listą godzin, np. "2026-03-27-14,2026-03-27-15"
    semestr_id = Column(Integer, ForeignKey("semestr.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", backref="dezyderaty")
    semestr = relationship("Semestr", backref="dezyderaty")
