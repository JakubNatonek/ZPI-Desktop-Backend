from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.model_unavailability_note import UnavailabilityNote, NoteStatus, NoteType
from app.models.model_notification import Notification
from app.models.model_user import User
from app.models.model_role import Role


def create_unavailability_note(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date | None,
    description: str | None,
    note_type: str,
) -> UnavailabilityNote:
    """
    Tworzy notatkę o niedostępności.
    Automatycznie tworzy powiadomienia dla wszystkich adminów.
    """
    note = UnavailabilityNote(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        description=description.strip() if description else None,
        note_type=NoteType(note_type),
        status=NoteStatus.PENDING,
    )
    db.add(note)
    db.flush()  # Flush aby otrzymać ID

    # Pobierz autora (dzielę mu pełne imię i nazwisko)
    author = db.query(User).filter(User.user_id == user_id).first()
    if not author:
        db.rollback()
        raise ValueError(f"User with id {user_id} not found")

    # Utwórz powiadomienia dla wszystkich adminów
    _notify_admins_about_new_note(db, author, note)

    db.commit()
    db.refresh(note)
    return note


def get_unavailability_note_by_id(db: Session, note_id: int) -> UnavailabilityNote | None:
    """Pobiera notatkę po ID."""
    return db.query(UnavailabilityNote).filter(UnavailabilityNote.id == note_id).first()


def get_unavailability_notes_for_user(
    db: Session,
    user_id: int,
) -> list[UnavailabilityNote]:
    """Pobiera wszystkie notatki danego użytkownika."""
    return (
        db.query(UnavailabilityNote)
        .filter(UnavailabilityNote.user_id == user_id)
        .order_by(UnavailabilityNote.created_at.desc())
        .all()
    )


def get_all_unavailability_notes(db: Session) -> list[tuple[UnavailabilityNote, User]]:
    """Pobiera wszystkie notatki z informacją o autorze (dla admina)."""
    return (
        db.query(UnavailabilityNote, User)
        .join(User, UnavailabilityNote.user_id == User.user_id)
        .order_by(UnavailabilityNote.created_at.desc())
        .all()
    )


def get_pending_unavailability_notes(db: Session) -> list[tuple[UnavailabilityNote, User]]:
    """Pobiera wszystkie notatki o statusie 'pending' z informacją o autorze."""
    return (
        db.query(UnavailabilityNote, User)
        .join(User, UnavailabilityNote.user_id == User.user_id)
        .filter(UnavailabilityNote.status == NoteStatus.PENDING)
        .order_by(UnavailabilityNote.created_at.desc())
        .all()
    )


def update_unavailability_note_status(
    db: Session,
    note_id: int,
    new_status: str,
) -> UnavailabilityNote | None:
    """
    Zmienia status notatki.
    Automatycznie tworzy powiadomienie dla autora notatki.
    """
    note = get_unavailability_note_by_id(db, note_id)
    if not note:
        return None

    old_status = note.status
    note.status = NoteStatus(new_status)
    note.updated_at = datetime.now(timezone.utc)
    db.add(note)
    db.flush()

    # Tworz powiadomienie dla autora notatki
    _notify_user_about_status_change(db, note.user_id, old_status, new_status)

    db.commit()
    db.refresh(note)
    return note


def get_active_notes_for_user(db: Session, user_id: int, today: date) -> list[UnavailabilityNote]:
    """
    Pobiera aktywne notatki dla danego użytkownika na dzień dzisiejszy.
    Notatka jest aktywna jeśli status to 'accepted' lub 'acknowledged'
    i dzisiejsza data mieści się w zakresie start_date do end_date.
    """
    return (
        db.query(UnavailabilityNote)
        .filter(
            UnavailabilityNote.user_id == user_id,
            UnavailabilityNote.status.in_([NoteStatus.ACCEPTED, NoteStatus.ACKNOWLEDGED]),
            UnavailabilityNote.start_date <= today,
            (UnavailabilityNote.end_date.is_(None) | (UnavailabilityNote.end_date >= today)),
        )
        .all()
    )


# ==================== Helper Functions ====================


def _notify_admins_about_new_note(db: Session, author: User, note: UnavailabilityNote) -> None:
    """
    Tworzy powiadomienia dla wszystkich adminów o nowej notatce.
    """
    print(f"[DEBUG] Creating admin notifications for note ID {note.id}")

    # Pobierz ID roli admin
    admin_role = db.query(Role).filter(Role.name.ilike("admin")).first()
    if not admin_role:
        print("[DEBUG] Admin role not found!")
        return

    print(f"[DEBUG] Found admin role: {admin_role.id}")

    # Pobierz wszystkich użytkowników z rolą admin
    from app.models.model_role_for_user import RolesForUser
    admin_users = (
        db.query(User)
        .join(RolesForUser, User.user_id == RolesForUser.user_id)
        .filter(RolesForUser.role_id == admin_role.id)
        .all()
    )

    print(f"[DEBUG] Found {len(admin_users)} admins")

    note_type_display = "prośbę o wolne" if note.note_type == NoteType.REQUEST else "nieobecność"
    start_date_str = note.start_date.strftime("%Y-%m-%d")
    end_date_str = f" do {note.end_date.strftime('%Y-%m-%d')}" if note.end_date else ""

    message = (
        f"Nowa notatka o niedostępności od {author.first_name} {author.last_name}. "
        f"Typ: {note_type_display}. Okres: {start_date_str}{end_date_str}."
    )

    print(f"[DEBUG] Message: {message}")

    for admin_user in admin_users:
        print(f"[DEBUG] Creating notification for admin: {admin_user.user_id}")
        notification = Notification(
            user_id=admin_user.user_id,
            message=message,
            is_read=False,
        )
        db.add(notification)

    db.flush()
    print(f"[DEBUG] Notifications created")


def _notify_user_about_status_change(
    db: Session,
    user_id: int,
    old_status: NoteStatus | str,
    new_status: str,
) -> None:
    """
    Tworzy powiadomienie dla autora notatki o zmianie statusu.
    """
    status_messages = {
        "accepted": "zaakceptowana",
        "rejected": "odrzucona",
        "acknowledged": "zapoznano się",
    }

    status_display = status_messages.get(new_status, new_status)
    message = f"Status Twojej notatki o niedostępności zmienił się na: {status_display}."

    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False,
    )
    db.add(notification)
    db.flush()
