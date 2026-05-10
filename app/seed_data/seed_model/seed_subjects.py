from sqlalchemy.orm import Session
from sqlalchemy import text

from app.cruds.crud_activity import get_or_create_activity
from app.schemas.subject import SubjectCreate
from app.cruds.crud_subject import create_subject


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
	{"id": 14, "name": "Zespołowe przedsięwzięcie inżynierskie", "activity": "projekty", "type_display": "P", "room_properties": "", "blocked": False, "periodic": True},
    {"id": 15, "name": "Seminarium dyplomowe/Przygotowanie pracy dyplomowej", "activity": "seminaria", "type_display": "S", "room_properties": "", "blocked": False, "periodic": True},
    {"id": 16, "name": "Teoria podejmowania decyzji", "activity": "wyklady", "type_display": "W", "room_properties": "", "blocked": False, "periodic": True},
]


def seed_subjects(db: Session) -> None:
	"""Seed subjects table with example data and linked activity types."""

	created_count = 0
	for payload in SAMPLE_SUBJECTS:
		subject_name = payload["name"]
		activity_name = payload["activity"]
		type_display = payload["type_display"]
		room_properties = payload["room_properties"]
		blocked = payload["blocked"]
		periodic = payload["periodic"]

		activity = get_or_create_activity(db, activity_name)
		if activity.id is None:
			continue

		try:
			subject = create_subject(
				db,
				SubjectCreate(
					name=subject_name,
					activity_id=activity.id,
					type_display=type_display,
					room_properties=room_properties,
					blocked=blocked,
					periodic=periodic,
				)
			)
			created_count += 1
		except Exception:
			continue

	db.execute(
		text(
			"SELECT setval(pg_get_serial_sequence('subject', 'id'), COALESCE((SELECT MAX(id) FROM subject), 0) + 1, false)"
		)
	)
	db.commit()
	print(f"Subjects seeded. Added: {created_count}")