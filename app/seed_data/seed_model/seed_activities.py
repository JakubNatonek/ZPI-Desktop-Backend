from sqlalchemy.orm import Session

from app.cruds.crud_activity import get_or_create_activity


ACTIVITY_NAMES = [
    "laboratoria",
    "konferencje",
    "seminaria",
    "wykłady",
    "ćwiczenia",
    "warsztaty",
    "egzaminy",
    "konsultacje",
    "projekty",
]


def seed_activities(db: Session) -> None:
    ensured_count = 0
    for activity_name in ACTIVITY_NAMES:
        activity = get_or_create_activity(db, activity_name)
        if activity.id is not None:
            ensured_count += 1

    db.commit()
    print(f"Activities seeded. Total ensured: {ensured_count}")