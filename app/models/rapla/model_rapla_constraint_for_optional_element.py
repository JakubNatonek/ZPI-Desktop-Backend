from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class RaplaConstraintForOptionalElement(Base):
    __tablename__ = "rapla_constraint_for_optional_element"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    optional_element_id = Column(Integer, ForeignKey("rapla_optional_element.id"), index=True, nullable=False)
    constraint_id = Column(Integer, ForeignKey("rapla_constraint.id"), index=True, nullable=False)

    optional_element = relationship("RaplaOptionalElement")
    constraint = relationship("RaplaConstraint")

    __table_args__ = (
        UniqueConstraint("optional_element_id", "constraint_id", name="uq_rapla_constraint_for_optional_element"),
    )
