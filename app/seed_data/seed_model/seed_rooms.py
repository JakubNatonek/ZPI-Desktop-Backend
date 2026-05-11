from sqlalchemy.orm import Session
from sqlalchemy import text

from app.cruds.crud_activity import get_or_create_activity
from app.cruds.crud_department import get_department_by_abbreviation
from app.cruds.room.crud_room_type import get_or_create_room_type
from app.cruds.room.crud_room import create_room_for_seed
from app.cruds.crud_special_equipment import get_or_create_special_equipment
from app.models.model_room import Room


def seed_rooms(db: Session) -> None:
	"""Seed rooms table with sample data."""
	rooms = [
		{"id": 1, "number": "101", "seats": 30, "description": "Sala wykładowa", "room_type_name": "Wykładowa", "departments": ["WE", "WSiS"], "activities": ["wykłady", "seminaria"], "special_equipment": ["Projektor", "Ekran", "Nagłośnienie"]},
		{"id": 2, "number": "102", "seats": 20, "description": "Laboratorium komputerowe", "room_type_name": "Laboratoryjna", "departments": ["WI", "WLiZ"], "activities": ["ćwiczenia", "laboratoria"], "special_equipment": ["Komputer", "Projektor", "Tablica interaktywna"]},
		{"id": 3, "number": "201", "seats": 50, "description": "Aula", "room_type_name": "Wykładowa", "departments": ["WE"], "activities": ["wykłady"], "special_equipment": ["Projektor", "Mikrofon", "Nagłośnienie"]},
		{"id": 4, "number": "101", "seats": 25, "description": "Sala ćwiczeniowa", "room_type_name": "Ćwiczeniowa", "departments": ["WSiS"], "activities": ["ćwiczenia", "seminaria"], "special_equipment": ["Flipchart", "Tablica interaktywna"]},
		{"id": 5, "number": "102", "seats": 15, "description": "Laboratorium fizyczne", "room_type_name": "Laboratoryjna", "departments": ["WI"], "activities": ["laboratoria"], "special_equipment": ["Komputer", "Klimatyzacja"]},
		{"id": 6, "number": "001", "seats": 100, "description": "Duża aula", "room_type_name": "Wykładowa", "departments": ["WKFiB", "WLiZ"], "activities": ["wykłady", "konferencje"], "special_equipment": ["Projektor", "Ekran", "Nagłośnienie", "Mikrofon"]},
	]

	created_count = 0
	for room in rooms:
		exists = db.query(Room).filter_by(id=room["id"]).first()
		if not exists:
			room_type_name = room["room_type_name"]
			room_type = get_or_create_room_type(db, room_type_name)
			department_entities = [
				get_department_by_abbreviation(db, abbreviation)
				for abbreviation in room["departments"]
			]
			department_ids = [department.id for department in department_entities if department is not None and department.id is not None]
			activity_ids = [
				activity.id
				for activity in [get_or_create_activity(db, activity_name) for activity_name in room["activities"]]
				if activity.id is not None
			]
			special_equipment_ids = [
				equipment.id
				for equipment in [get_or_create_special_equipment(db, equipment_name) for equipment_name in room["special_equipment"]]
				if equipment.id is not None
			]

			create_room_for_seed(
				db,
				room_id=room["id"],
				room_number=room["number"],
				seats_count=room["seats"],
				room_type_id=room_type.id,
				departments=department_ids,
				activities=activity_ids,
				special_equipment=special_equipment_ids,
				description=room["description"],
			)
			created_count += 1

	db.commit()
	db.execute(
		text(
			"SELECT setval(pg_get_serial_sequence('room', 'id'), COALESCE((SELECT MAX(id) FROM room), 0) + 1, false)"
		)
	)
	db.commit()
	print(f"Rooms seeded. Added: {created_count}")