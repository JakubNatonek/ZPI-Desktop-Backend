from sqlalchemy.orm import Session

from app.cruds.crud_activity import get_or_create_activity
from app.models.model_subject import Subject
from app.models.model_subject_activity import SubjectActivity


SAMPLE_SUBJECTS = [
	{"id": 1, "name": "Programowanie obiektowe", "activity": "wyklady", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
	{"id": 2, "name": "Programowanie obiektowe", "activity": "laboratoria", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
	{"id": 3, "name": "Bazy danych", "activity": "wyklady", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
	{"id": 4, "name": "Bazy danych", "activity": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
	{"id": 5, "name": "Algorytmy i struktury danych", "activity": "wyklady", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
	{"id": 6, "name": "Algorytmy i struktury danych", "activity": "laboratoria", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
	{"id": 7, "name": "Systemy operacyjne", "activity": "laboratoria", "type_display": "L", "room_properties": "komputerowa", "blocked": False, "periodic": True},
	{"id": 8, "name": "Systemy operacyjne", "activity": "projekty", "type_display": "P", "room_properties": "projektowa", "blocked": False, "periodic": True},
	{"id": 9, "name": "Inzynieria oprogramowania", "activity": "seminaria", "type_display": "S", "room_properties": "seminaryjna", "blocked": False, "periodic": True},
	{"id": 10, "name": "Inzynieria oprogramowania", "activity": "projekty", "type_display": "P", "room_properties": "projektowa", "blocked": False, "periodic": True},
	{"id": 11, "name": "Matematyka dyskretna", "activity": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
	{"id": 12, "name": "Matematyka dyskretna", "activity": "konsultacje", "type_display": "K", "room_properties": "konsultacyjna", "blocked": False, "periodic": False},
]


def seed_subjects(db: Session) -> None:
	"""Seed subjects table with example data and linked activity types."""

	created_count = 0
	updated_count = 0
	link_count = 0
	for payload in SAMPLE_SUBJECTS:
		subject_id = payload["id"]
		subject_name = payload["name"]
		activity_name = payload["activity"]
		type_display = payload["type_display"]
		room_properties = payload["room_properties"]
		blocked = payload["blocked"]
		periodic = payload["periodic"]

		subject = db.query(Subject).filter_by(id=subject_id).first()
		if subject is None:
			subject = Subject(
				id=subject_id,
				name=subject_name,
				type_id=None,
				type_display=type_display,
				room_properties=room_properties,
				blocked=blocked,
				periodic=periodic,
			)
			db.add(subject)
			db.flush()
			created_count += 1
		else:
			subject.name = subject_name
			subject.type_display = type_display
			subject.room_properties = room_properties
			subject.blocked = blocked
			subject.periodic = periodic
			updated_count += 1

		activity = get_or_create_activity(db, activity_name)
		link = (
			db.query(SubjectActivity)
			.filter(
				SubjectActivity.subject_id == subject.id,
				SubjectActivity.activity_id == activity.id,
			)
			.first()
		)
		if link is None:
			link = SubjectActivity(subject_id=subject.id, activity_id=activity.id)
			db.add(link)
			db.flush()
			link_count += 1

		subject.type_id = link.id
		db.add(subject)

		(
			db.query(SubjectActivity)
			.filter(
				SubjectActivity.subject_id == subject.id,
				SubjectActivity.id != link.id,
			)
			.delete(synchronize_session=False)
		)

	db.commit()
	print(f"Subjects seeded. Added: {created_count}, Updated: {updated_count}, Links added: {link_count}")