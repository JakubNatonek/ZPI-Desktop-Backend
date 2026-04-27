from sqlalchemy.orm import Session

from app.cruds.crud_field_of_study import get_or_create_field_of_study
from app.cruds.crud_subject_for_field_of_study import add_subject_to_field_of_study
from app.models.model_subject import Subject


FIELD_OF_STUDY_SEED = [
	{
		"name": "Informatyka Stosowana",
		"abbrevation": "IS",
		"year": 1,
		"subject_ids": [1, 2, 3, 4, 5, 6, 7, 8],
	},
	{
		"name": "Informatyka Stosowana",
		"abbrevation": "IS",
		"year": 2,
		"subject_ids": [1, 3, 5, 7, 9, 10, 11, 12],
	},
]


def seed_field_of_study(db: Session) -> None:
	ensured_fields = 0
	ensured_mappings = 0

	for entry in FIELD_OF_STUDY_SEED:
		field_of_study = get_or_create_field_of_study(
			db,
			name=entry["name"],
			abbrevation=entry["abbrevation"],
			year=entry["year"],
		)
		if field_of_study.id is None:
			continue

		ensured_fields += 1

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
		f"Fields ensured: {ensured_fields}, Mappings ensured: {ensured_mappings}"
	)
 