from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_field_of_study import FieldOfStudy
from app.models.model_subject import Subject
from app.models.model_subject_for_field_of_study import SubjectForFieldOfStudy
from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study
from app.cruds.rapla.crud_rapla_permission import create_permission, get_permission_by_access_and_group
from app.cruds.rapla.crud_rapla_permission_for_resourc import create_permission_for_resourc


def get_subject_field_mapping(
	db: Session,
	subject_id: int,
	field_of_study_id: int,
) -> Optional[SubjectForFieldOfStudy]:
	return (
		db.query(SubjectForFieldOfStudy)
		.filter(
			SubjectForFieldOfStudy.subject_id == subject_id,
			SubjectForFieldOfStudy.field_of_study_id == field_of_study_id,
		)
		.first()
	)


def _ensure_department_permissions_for_subject(
	db: Session,
	subject_id: int,
	field_of_study_id: int,
) -> None:
	from app.cruds.rapla.crud_rapla_subject_to_resourc import get_resourc_by_subject_id

	resource = get_resourc_by_subject_id(db, subject_id)
	if resource is None or resource.id is None:
		return

	departments = get_departments_for_field_of_study(db, field_of_study_id)
	for department in departments:
		abbreviation = getattr(department, "abbreviation", None)
		if not abbreviation:
			continue

		group = f"category[key='{abbreviation}_Editor']"
		perm = get_permission_by_access_and_group(db, "allocate_conflicts", group)
		if perm is None:
			perm = create_permission(db, access="allocate_conflicts", group=group)

		try:
			create_permission_for_resourc(db, resource.id, perm.id)
		except Exception:
			continue


def add_subject_to_field_of_study(
	db: Session,
	subject_id: int,
	field_of_study_id: int,
) -> SubjectForFieldOfStudy:
	existing = get_subject_field_mapping(db, subject_id, field_of_study_id)
	if existing is not None:
		_ensure_department_permissions_for_subject(db, subject_id, field_of_study_id)
		return existing

	mapping = SubjectForFieldOfStudy(
		subject_id=subject_id,
		field_of_study_id=field_of_study_id,
	)
	db.add(mapping)
	db.flush()
	_ensure_department_permissions_for_subject(db, subject_id, field_of_study_id)
	return mapping


def get_subjects_for_field_of_study(db: Session, field_of_study_id: int) -> list[Subject]:
	return (
		db.query(Subject)
		.join(SubjectForFieldOfStudy, Subject.id == SubjectForFieldOfStudy.subject_id)
		.filter(SubjectForFieldOfStudy.field_of_study_id == field_of_study_id)
		.order_by(Subject.name.asc(), Subject.id.asc())
		.all()
	)


def get_primary_field_of_study_for_subject(db: Session, subject_id: int) -> FieldOfStudy | None:
	return (
		db.query(FieldOfStudy)
		.join(SubjectForFieldOfStudy, FieldOfStudy.id == SubjectForFieldOfStudy.field_of_study_id)
		.filter(SubjectForFieldOfStudy.subject_id == subject_id)
		.order_by(SubjectForFieldOfStudy.id.asc())
		.first()
	)
