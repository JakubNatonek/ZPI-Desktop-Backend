from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Dezyderata(Base):
    __tablename__ = "availability_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    data_od = Column(Date, nullable=False)
    data_do = Column(Date, nullable=False)
    semestr_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True)
    day_id = Column(Integer, ForeignKey("days.id", ondelete="RESTRICT"), nullable=False, index=True)
    from_hour = Column(Integer, nullable=False)
    to_hour = Column(Integer, nullable=False)
    is_available = Column(Boolean, nullable=False)

    user = relationship("User", backref="dezyderaty")
    semestr = relationship("Semestr", backref="dezyderaty")
    day = relationship("Day", backref="dezyderaty")
