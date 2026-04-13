from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.cruds.crud_announcement import create_announcement
from app.cruds.crud_user import get_user_by_login
from app.models.model_announcement import Announcement


POLAND_TIMEZONE = ZoneInfo("Europe/Warsaw")


DEFAULT_ANNOUNCEMENTS = [
    {
        "subject": "Start semestru zimowego",
        "content": "Rozpoczynamy zajecia zgodnie z harmonogramem. Sprawdzcie aktualne plany w systemie.",
        "created_at": datetime(2026, 2, 17, 8, 30, tzinfo=POLAND_TIMEZONE),
    },
    {
        "subject": "Zmiana sali dla cwiczen",
        "content": "Cwiczenia z programowania zostaly przeniesione do sali B-102. Obowiazuje od najblizszego tygodnia.",
        "created_at": datetime(2026, 2, 18, 12, 15, tzinfo=POLAND_TIMEZONE),
    },
    {
        "subject": "Dyzur konsultacyjny",
        "content": "W srode od 10:00 do 12:00 odbedzie sie dyzur konsultacyjny dla studentow.",
        "created_at": datetime(2026, 2, 19, 10, 0, tzinfo=POLAND_TIMEZONE),
    },
    {
        "subject": "Termin oddania projektu",
        "content": "Ostateczny termin oddania projektu zaliczeniowego mija w piatek o 23:59.",
        "created_at": datetime(2026, 2, 20, 16, 45, tzinfo=POLAND_TIMEZONE),
    },
    {
        "subject": "Przerwa techniczna",
        "content": "W weekend planowana jest krotka przerwa techniczna systemu. Prosze zapisac prace z wyprzedzeniem.",
        "created_at": datetime(2026, 2, 21, 18, 0, tzinfo=POLAND_TIMEZONE),
    },
]


def seed_announcements(db: Session, author_id: int | None = None) -> None:
    if author_id is None:
        admin_user = get_user_by_login(db, "admin")
        if admin_user is None:
            raise RuntimeError("Admin user not found. Run seed_admin first or pass author_id.")
        author_id = admin_user.user_id

    created_count = 0
    for announcement_data in DEFAULT_ANNOUNCEMENTS:
        existing = (
            db.query(Announcement)
            .filter(Announcement.subject == announcement_data["subject"])
            .first()
        )
        if existing is not None:
            continue

        create_announcement(
            db,
            author_id=author_id,
            subject=announcement_data["subject"],
            content=announcement_data["content"],
            created_at=announcement_data["created_at"],
        )
        created_count += 1

    print(f"Announcements seeded. Added: {created_count}")
