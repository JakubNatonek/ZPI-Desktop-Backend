from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_field_of_study import FieldOfStudy
from app.models.model_subject import Subject
from app.models.model_subject_for_field_of_study import SubjectForFieldOfStudy


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


def add_subject_to_field_of_study(
	db: Session,
	subject_id: int,
	field_of_study_id: int,
) -> SubjectForFieldOfStudy:
	existing = get_subject_field_mapping(db, subject_id, field_of_study_id)
	if existing is not None:
		return existing

	mapping = SubjectForFieldOfStudy(
		subject_id=subject_id,
		field_of_study_id=field_of_study_id,
	)
	db.add(mapping)
	db.flush()
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
