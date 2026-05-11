from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class DepartmentForFieldOfStudy(Base):
	__tablename__ = "department_for_field_of_study"
	__table_args__ = (
		UniqueConstraint("department_id", "field_of_study_id", name="uq_department_field_of_study"),
	)

	id = Column(Integer, primary_key=True, index=True, autoincrement=True)
	department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
	field_of_study_id = Column(Integer, ForeignKey("field_of_study.id"), nullable=False, index=True)

	department = relationship("Department", back_populates="field_of_study_links")
	field_of_study = relationship("FieldOfStudy", back_populates="department_links")
