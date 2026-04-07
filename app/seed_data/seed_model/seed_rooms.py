from sqlalchemy.orm import Session

from app.models.model_room import Room


def seed_rooms(db: Session) -> None:
	"""Seed rooms table with sample data."""
	rooms = [
		{"id": 1, "building": "A", "number": "101", "seats": 30, "description": "Sala wykladowa", "type": "wykladowa", "activities": "wyklad,seminarium"},
		{"id": 2, "building": "A", "number": "102", "seats": 20, "description": "Laboratorium komputerowe", "type": "laboratorium", "activities": "cwiczenia,laboratorium"},
		{"id": 3, "building": "A", "number": "201", "seats": 50, "description": "Aula", "type": "wykladowa", "activities": "wyklad"},
		{"id": 4, "building": "B", "number": "101", "seats": 25, "description": "Sala cwiczeniowa", "type": "cwiczeniowa", "activities": "cwiczenia,seminarium"},
		{"id": 5, "building": "B", "number": "102", "seats": 15, "description": "Laboratorium fizyczne", "type": "laboratorium", "activities": "laboratorium"},
		{"id": 6, "building": "C", "number": "001", "seats": 100, "description": "Duza aula", "type": "wykladowa", "activities": "wyklad,konferencja"},
	]

	created_count = 0
	for room in rooms:
		exists = db.query(Room).filter_by(id=room["id"]).first()
		if not exists:
			db.add(Room(**room))
			created_count += 1

	db.commit()
	print(f"Rooms seeded. Added: {created_count}")