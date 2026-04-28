from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaSubjectToResourc(Base):
    __tablename__ = "rapla_subject_to_resourc"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subject.id"), index=True, nullable=False)
    rapla_resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), index=True, nullable=False)

    subject = relationship("Subject")
    rapla_resourc = relationship("ModelRaplaResourc")

    __table_args__ = (
        UniqueConstraint("subject_id", "rapla_resourc_id", name="uq_rapla_subject_to_resourc"),
    )
