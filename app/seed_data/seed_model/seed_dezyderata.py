from datetime import date

from sqlalchemy.orm import Session

from app.models.model_dezyderata import Dezyderata


def seed_dezyderata(db: Session) -> None:
	"""Create sample availability preferences for existing sample users."""
	entries = [
		{
			"user_id": 2,
			"data_od": date(2025, 10, 1),
			"data_do": date(2026, 2, 15),
			"semestr_id": 1,
			"day_id": 1,
			"from_hour": 8,
			"to_hour": 15,
			"is_available": True,
		},
		{
			"user_id": 2,
			"data_od": date(2025, 9, 26),
			"data_do": date(2026, 2, 10),
			"semestr_id": 1,
			"day_id": 2,
			"from_hour": 9,
			"to_hour": 13,
			"is_available": True,
		},
		{
			"user_id": 3,
			"data_od": date(2025, 9, 28),
			"data_do": date(2026, 2, 12),
			"semestr_id": 1,
			"day_id": 3,
			"from_hour": 10,
			"to_hour": 14,
			"is_available": False,
		},
		{
			"user_id": 2,
			"data_od": date(2025, 10, 4),
			"data_do": date(2026, 2, 18),
			"semestr_id": 1,
			"day_id": 4,
			"from_hour": 12,
			"to_hour": 17,
			"is_available": True,
		},
		{
			"user_id": 3,
			"data_od": date(2025, 10, 6),
			"data_do": date(2026, 2, 20),
			"semestr_id": 1,
			"day_id": 5,
			"from_hour": 8,
			"to_hour": 12,
			"is_available": True,
		},
		{
			"user_id": 3,
			"data_od": date(2025, 9, 30),
			"data_do": date(2026, 2, 14),
			"semestr_id": 1,
			"day_id": 6,
			"from_hour": 13,
			"to_hour": 18,
			"is_available": False,
		},
	]

	created_count = 0
	for entry in entries:
		exists = (
			db.query(Dezyderata)
			.filter_by(user_id=entry["user_id"], semestr_id=entry["semestr_id"], day_id=entry["day_id"])
			.first()
		)
		if exists is not None:
			continue

		db.add(Dezyderata(**entry))
		created_count += 1

	db.commit()
	print(f"Dezyderaty seeded. Added: {created_count}")