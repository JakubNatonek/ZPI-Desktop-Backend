from sqlalchemy.orm import Session

from app.models.model_group import Group


def seed_groups(db: Session) -> None:
	"""Seed groups table with sample data."""
	groups = [
		{"id": 1, "specialization": "Informatyka Stosowana", "code": "IS1", "year": 1, "studies_type": "stacjonarne"},
		{"id": 2, "specialization": "Informatyka Stosowana", "code": "IS2", "year": 2, "studies_type": "stacjonarne"},
		{"id": 3, "specialization": "Informatyka Stosowana", "code": "IS3", "year": 3, "studies_type": "stacjonarne"},
		{"id": 4, "specialization": "Systemy Komputerowe", "code": "SK1", "year": 1, "studies_type": "stacjonarne"},
		{"id": 5, "specialization": "Systemy Komputerowe", "code": "SK2", "year": 2, "studies_type": "niestacjonarne"},
	]

	created_count = 0
	for group in groups:
		exists = db.query(Group).filter_by(id=group["id"]).first()
		if not exists:
			db.add(Group(**group))
			created_count += 1

	db.commit()
	print(f"Groups seeded. Added: {created_count}")