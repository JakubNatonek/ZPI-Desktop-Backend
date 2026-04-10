from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaSemesterToResourc(Base):
    __tablename__ = "rapla_semesters_to_resourc"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), index=True, nullable=False)
    rapla_resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), index=True, nullable=False)

    semester = relationship("Semestr")
    rapla_resourc = relationship("ModelRaplaResourc")

    __table_args__ = (
        UniqueConstraint("semester_id", "rapla_resourc_id", name="uq_rapla_semester_to_resourc"),
    )
