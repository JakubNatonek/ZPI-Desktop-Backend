from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class ModelFieldOfStudyForGroup(Base):
    __tablename__ = "field_of_study_for_group"
    __table_args__ = (
        UniqueConstraint("field_of_study_id", "group_id", name="uq_field_of_study_for_group"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    field_of_study_id = Column(Integer, ForeignKey("field_of_study.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False, index=True)

    # simple convenience relationships (no back_populates to avoid coupling)
    group = relationship("Group")
    field_of_study = relationship("FieldOfStudy")
