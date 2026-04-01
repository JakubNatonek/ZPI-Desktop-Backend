from datetime import date

from sqlalchemy.orm import Session

from app.models.model_dezyderata import Dezyderata


def seed_dezyderata(db: Session) -> None:
    """Create a default availability preference for user_id=2, semestr_id=1, day_id=1."""
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
        }
    ]

    created_count = 0
    for e in entries:
        exists = db.query(Dezyderata).filter_by(user_id=e["user_id"], semestr_id=e["semestr_id"], day_id=e["day_id"]).first()
        if not exists:
            db.add(Dezyderata(**e))
            created_count += 1

    db.commit()
    print(f"Dezyderaty seeded. Added: {created_count}")
