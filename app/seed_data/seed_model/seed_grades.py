import random

from sqlalchemy.orm import Session

from app.models.model_grade import GradeRecord
from app.models.model_subject import Subject


def seed_grades(db: Session) -> None:
	"""Seed three grades for users 1 and 2 using random subjects."""
	rng = random.Random(42)
	subjects = db.query(Subject).order_by(Subject.id.asc()).all()
	if len(subjects) < 3:
		print("Grades seeded: skipped because there are not enough subjects.")
		return

	grade_values = [3.5, 4.0, 4.5, 5.0]
	created_count = 0

	for student_id in (1, 2):
		selected_subjects = rng.sample(subjects, 3)
		for sort_order, subject in enumerate(selected_subjects, start=1):
			activity_name = ""
			if subject.type_link is not None and subject.type_link.activity is not None:
				activity_name = str(subject.type_link.activity.name)

			existing = (
				db.query(GradeRecord)
				.filter(
					GradeRecord.student_id == student_id,
					GradeRecord.subject_name == subject.name,
					GradeRecord.sort_order == sort_order,
				)
				.first()
			)
			if existing is not None:
				continue

			db.add(
				GradeRecord(
					student_id=student_id,
					lecturer_id=3,
					semester=1,
					subject_name=subject.name,
					component_label=f"Zadanie {sort_order}",
					component_info=subject.type_display or activity_name,
					grade_value=rng.choice(grade_values),
					is_final=sort_order == 3,
					sort_order=sort_order,
				)
			)
			created_count += 1

	db.commit()
	print(f"Grades seeded. Added: {created_count}")