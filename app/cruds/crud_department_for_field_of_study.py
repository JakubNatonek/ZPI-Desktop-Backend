from sqlalchemy.orm import Session

from app.models.model_department import Department
from app.models.model_department_for_field_of_study import DepartmentForFieldOfStudy


def get_department_field_mapping(
	db: Session,
	department_id: int,
	field_of_study_id: int,
) -> DepartmentForFieldOfStudy | None:
	return (
		db.query(DepartmentForFieldOfStudy)
		.filter(
			DepartmentForFieldOfStudy.department_id == department_id,
			DepartmentForFieldOfStudy.field_of_study_id == field_of_study_id,
		)
		.first()
	)


def add_department_to_field_of_study(
	db: Session,
	department_id: int,
	field_of_study_id: int,
) -> DepartmentForFieldOfStudy:
	existing = get_department_field_mapping(db, department_id, field_of_study_id)
	if existing is not None:
		return existing

	mapping = DepartmentForFieldOfStudy(
		department_id=department_id,
		field_of_study_id=field_of_study_id,
	)
	db.add(mapping)
	db.flush()
	return mapping


def get_departments_for_field_of_study(db: Session, field_of_study_id: int) -> list[Department]:
	return (
		db.query(Department)
		.join(
			DepartmentForFieldOfStudy,
			Department.id == DepartmentForFieldOfStudy.department_id,
		)
		.filter(DepartmentForFieldOfStudy.field_of_study_id == field_of_study_id)
		.order_by(Department.abbreviation.asc(), Department.id.asc())
		.all()
	)
