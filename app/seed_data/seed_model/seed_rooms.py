from sqlalchemy.orm import Session
from sqlalchemy import text

from app.cruds.crud_activity import get_or_create_activity
from app.cruds.crud_room_type import get_room_type_by_name
from app.models.model_room import Room


def seed_rooms(db: Session) -> None:
	"""Seed rooms table with sample data."""
	rooms = [
		{"id": 1, "building": "A", "number": "101", "seats": 30, "description": "Sala wykładowa", "type": "Wykładowa", "activities": ["wykłady", "seminaria"]},
		{"id": 2, "building": "A", "number": "102", "seats": 20, "description": "Laboratorium komputerowe", "type": "Laboratoryjna", "activities": ["ćwiczenia", "laboratoria"]},
		{"id": 3, "building": "A", "number": "201", "seats": 50, "description": "Aula", "type": "Wykładowa", "activities": ["wykłady"]},
		{"id": 4, "building": "B", "number": "101", "seats": 25, "description": "Sala ćwiczeniowa", "type": "Ćwiczeniowa", "activities": ["ćwiczenia", "seminaria"]},
		{"id": 5, "building": "B", "number": "102", "seats": 15, "description": "Laboratorium fizyczne", "type": "Laboratoryjna", "activities": ["laboratoria"]},
		{"id": 6, "building": "C", "number": "001", "seats": 100, "description": "Duża aula", "type": "Wykładowa", "activities": ["wykłady", "konferencje"]},
	]

	created_count = 0
	for room in rooms:
		exists = db.query(Room).filter_by(id=room["id"]).first()
		if not exists:
			room_type = get_room_type_by_name(db, room["type"])
			new_room = Room(
				id=room["id"],
				building=room["building"],
				number=room["number"],
				seats=room["seats"],
				description=room["description"],
				type=room_type,
			)
			new_room.activities = [get_or_create_activity(db, activity_name) for activity_name in room["activities"]]
			db.add(new_room)
			created_count += 1

	db.commit()
	db.execute(
		text(
			"SELECT setval(pg_get_serial_sequence('room', 'id'), COALESCE((SELECT MAX(id) FROM room), 0) + 1, false)"
		)
	)
	db.commit()
	print(f"Rooms seeded. Added: {created_count}")