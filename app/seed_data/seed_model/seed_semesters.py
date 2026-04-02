from datetime import date

from sqlalchemy.orm import Session

from app.models.model_semestr import Semestr


def seed_semesters(db: Session):
    """Seed semesters table with sample data."""
    semesters = [
        {"nazwa": "Semestr zimowy 2025/2026", "data_rozpoczecia": date(2025, 10, 1), "data_zakonczenia": date(2026, 2, 15)},
        {"nazwa": "Semestr letni 2025/2026", "data_rozpoczecia": date(2026, 2, 17), "data_zakonczenia": date(2026, 6, 30)},
        {"nazwa": "Semestr zimowy 2026/2027", "data_rozpoczecia": date(2026, 10, 1), "data_zakonczenia": date(2027, 2, 15)},
    ]

    created_count = 0
    for sem in semesters:
        exists = db.query(Semestr).filter_by(
            nazwa=sem["nazwa"],
            data_rozpoczecia=sem["data_rozpoczecia"],
            data_zakonczenia=sem["data_zakonczenia"],
        ).first()
        if not exists:
            db.add(Semestr(**sem))
            created_count += 1
    db.commit()
    print(f"Semesters seeded. Added: {created_count}")


