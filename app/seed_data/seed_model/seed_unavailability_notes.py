from datetime import date

from sqlalchemy.orm import Session

from app.models.model_unavailability_note import UnavailabilityNote, NoteType, NoteStatus


SAMPLE_NOTES = [
    # --- Wykładowca user_id=2 ---
    {
        "user_id": 2,
        "start_date": date(2026, 5, 20),
        "end_date": date(2026, 5, 22),
        "description": "Konferencja naukowa w Krakowie",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.ACCEPTED,
    },
    {
        "user_id": 2,
        "start_date": date(2026, 6, 3),
        "end_date": None,
        "description": "Urlop wypoczynkowy",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.PENDING,
    },
    {
        "user_id": 2,
        "start_date": date(2026, 7, 14),
        "end_date": date(2026, 7, 18),
        "description": "Wyjazd badawczy – wizyta w laboratorium partnerskim",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.PENDING,
    },
    {
        "user_id": 2,
        "start_date": date(2026, 5, 12),
        "end_date": date(2026, 5, 14),
        "description": "Zwolnienie lekarskie",
        "note_type": NoteType.FORCED,
        "status": NoteStatus.ACKNOWLEDGED,
    },
    # --- Wykładowca user_id=3 ---
    {
        "user_id": 3,
        "start_date": date(2026, 6, 15),
        "end_date": date(2026, 6, 19),
        "description": "Udział w komisji doktorskiej",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.PENDING,
    },
    {
        "user_id": 3,
        "start_date": date(2026, 5, 28),
        "end_date": None,
        "description": "Wyjazd służbowy – spotkanie z partnerem przemysłowym",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.REJECTED,
    },
    {
        "user_id": 3,
        "start_date": date(2026, 5, 5),
        "end_date": date(2026, 5, 9),
        "description": "Hospitalizacja",
        "note_type": NoteType.FORCED,
        "status": NoteStatus.PENDING,
    },
    {
        "user_id": 3,
        "start_date": date(2026, 8, 4),
        "end_date": date(2026, 8, 8),
        "description": "Letnia szkoła letnia – prowadzenie warsztatów",
        "note_type": NoteType.REQUEST,
        "status": NoteStatus.ACCEPTED,
    },
]


def seed_unavailability_notes(db: Session) -> None:
    """Create sample unavailability notes for seeded lecturer users (idempotent)."""
    created = 0
    for entry in SAMPLE_NOTES:
        existing = (
            db.query(UnavailabilityNote)
            .filter(
                UnavailabilityNote.user_id == entry["user_id"],
                UnavailabilityNote.start_date == entry["start_date"],
                UnavailabilityNote.note_type == entry["note_type"],
            )
            .first()
        )
        if existing is None:
            note = UnavailabilityNote(**entry)
            db.add(note)
            created += 1

    db.commit()
    print(f"seed_unavailability_notes: {created} nowych notatek dodano.")
