from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubjectForFieldOfStudy(Base):
	__tablename__ = "subject_for_field_of_study"
	__table_args__ = (
		UniqueConstraint("subject_id", "field_of_study_id", name="uq_subject_field_of_study"),
	)

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	subject_id = Column(Integer, ForeignKey("subject.id", ondelete="CASCADE"), nullable=False, index=True)
	field_of_study_id = Column(Integer, ForeignKey("field_of_study.id", ondelete="CASCADE"), nullable=False, index=True)

	subject = relationship("Subject", back_populates="field_links")
	field_of_study = relationship("FieldOfStudy", back_populates="subject_links")
