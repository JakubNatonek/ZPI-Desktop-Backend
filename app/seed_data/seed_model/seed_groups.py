from sqlalchemy.orm import Session

from app.models.model_group import Group


def seed_groups(db: Session) -> None:
	"""Seed groups table with sample data."""
	groups = [
		{"id": 1, "specialization": "WI", "code": "IS", "year": 2023, "studies_type": "s"},
		{"id": 2, "specialization": "WI", "code": "IS", "year": 2023, "studies_type": "z"},
		{"id": 3, "specialization": "WI", "code": "IS", "year": 2024, "studies_type": "s"},
		{"id": 4, "specialization": "WI", "code": "IS", "year": 2024, "studies_type": "z"},
		{"id": 5, "specialization": "WI", "code": "IS", "year": 2025, "studies_type": "s"},
		{"id": 6, "specialization": "WI", "code": "IS", "year": 2025, "studies_type": "z"},
	]

	created_count = 0
	for group in groups:
		exists = db.query(Group).filter_by(id=group["id"]).first()
		if not exists:
			db.add(Group(**group))
			created_count += 1

	db.commit()
	print(f"Groups seeded. Added: {created_count}")