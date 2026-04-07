from sqlalchemy.orm import Session

from app.models.model_day import Day


def seed_days(db: Session):
    """Seed days table with week day IDs used by availability preferences."""
    days = [
        {"id": 1, "name": "monday"},
        {"id": 2, "name": "tuesday"},
        {"id": 3, "name": "wednesday"},
        {"id": 4, "name": "thursday"},
        {"id": 5, "name": "friday"},
        {"id": 6, "name": "saturday"},
        {"id": 7, "name": "sunday"},
    ]

    created_count = 0
    for day in days:
        exists = db.query(Day).filter_by(id=day["id"]).first()
        if not exists:
            db.add(Day(**day))
            created_count += 1

    db.commit()
    print(f"Days seeded. Added: {created_count}")


