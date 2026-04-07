from sqlalchemy.orm import Session

from app.models.model_subject import Subject


def seed_subjects(db: Session) -> None:
	"""Seed subjects table with sample data."""
	subjects = [
		{"id": 1, "name": "Programowanie obiektowe", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
		{"id": 2, "name": "Programowanie obiektowe", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
		{"id": 3, "name": "Bazy danych", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
		{"id": 4, "name": "Bazy danych", "type": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
		{"id": 5, "name": "Algorytmy i struktury danych", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
		{"id": 6, "name": "Algorytmy i struktury danych", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
		{"id": 7, "name": "Fizyka", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
		{"id": 8, "name": "Fizyka", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
		{"id": 9, "name": "Matematyka dyskretna", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
		{"id": 10, "name": "Matematyka dyskretna", "type": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
	]

	created_count = 0
	for subject in subjects:
		exists = db.query(Subject).filter_by(id=subject["id"]).first()
		if not exists:
			db.add(Subject(**subject))
			created_count += 1

	db.commit()
	print(f"Subjects seeded. Added: {created_count}")