from sqlalchemy.orm import Session

from app.cruds.crud_department import get_department_by_abbreviation
from app.cruds.crud_department_for_field_of_study import add_department_to_field_of_study
from app.cruds.crud_field_of_study import create_field_of_study
from app.cruds.crud_subject_for_field_of_study import add_subject_to_field_of_study
from app.models.model_field_of_study import FieldOfStudy
from app.models.model_subject import Subject


FIELD_OF_STUDY_SEED = [
	{
		"name": "Informatyka Stosowana",
		"abbrevation": "IS",
		"year": 1,
		"department": "WI",
		"subject_ids": [1, 2, 3, 4, 5, 6, 7, 8],
	},
	{
		"name": "Informatyka Stosowana",
		"abbrevation": "IS",
		"year": 2,
		"department": "WI",
		"subject_ids": [9, 10, 11, 12, 13, 14, 15],
	},
]


def seed_field_of_study(db: Session) -> None:
	ensured_fields = 0
	ensured_department_mappings = 0
	ensured_mappings = 0

	for entry in FIELD_OF_STUDY_SEED:
		field_of_study = create_field_of_study(
			db,
			name=entry["name"],
			abbrevation=entry["abbrevation"],
			year=entry["year"],
		)
		if field_of_study.id is None:
			continue

		ensured_fields += 1

		department = get_department_by_abbreviation(db, entry["department"])
		if department is not None and department.id is not None:
			mapping = add_department_to_field_of_study(
				db,
				department_id=department.id,
				field_of_study_id=field_of_study.id,
			)
			if mapping.id is not None:
				ensured_department_mappings += 1

		for subject_id in entry["subject_ids"]:
			subject = db.query(Subject).filter(Subject.id == subject_id).first()
			if subject is None or subject.id is None:
				continue

			mapping = add_subject_to_field_of_study(
				db,
				subject_id=subject.id,
				field_of_study_id=field_of_study.id,
			)
			if mapping.id is not None:
				ensured_mappings += 1

	db.commit()
	print(
		"Field of study seeded. "
		f"Fields ensured: {ensured_fields}, "
		f"Department mappings ensured: {ensured_department_mappings}, "
		f"Subject mappings ensured: {ensured_mappings}"
	)
 