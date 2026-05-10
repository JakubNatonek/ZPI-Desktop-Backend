from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaGroupToResourc(Base):
    __tablename__ = "rapla_group_to_resourc"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("group.id"), index=True, nullable=False)
    rapla_resourc_id = Column(Integer, ForeignKey("rapla_resourc.id"), index=True, nullable=False)

    group = relationship("Group")
    rapla_resourc = relationship("ModelRaplaResourc")

    __table_args__ = (
        UniqueConstraint("group_id", "rapla_resourc_id", name="uq_rapla_group_to_resourc"),
    )
