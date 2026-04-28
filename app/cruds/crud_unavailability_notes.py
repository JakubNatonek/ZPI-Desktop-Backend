from datetime import date, datetime, timezone
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.model_unavailability_note import UnavailabilityNote, NoteStatus, NoteType
from app.models.model_notification import Notification
from app.models.model_user import User
from app.models.model_role import Role


logger = logging.getLogger(__name__)


def create_unavailability_note(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date | None,
    description: str | None,
    note_type: str,
) -> tuple[UnavailabilityNote, list[Notification]]:
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
    created_notifications = _notify_admins_about_new_note(db, author, note)

    db.commit()
    db.refresh(note)
    return note, created_notifications


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
    note_type_value = note.note_type.value if hasattr(note.note_type, "value") else str(note.note_type)
    logger.info(
        "Creating admin notifications for unavailability note: note_id=%s author_user_id=%s author_name=%s note_type=%s start_date=%s end_date=%s",
        note.id,
        author.user_id,
        f"{author.first_name} {author.last_name}",
        note_type_value,
        note.start_date.isoformat(),
        note.end_date.isoformat() if note.end_date else None,
    )

    admin_users = get_admin_users_for_notifications(db, note_id=note.id)
    if not admin_users:
        logger.warning(
            "No admin users found while creating unavailability-note notifications: note_id=%s",
            note.id,
        )
        return []

    logger.info(
        "Found admins for unavailability-note notification fan-out: note_id=%s admin_count=%s",
        note.id,
        len(admin_users),
    )

    note_type_display = "prośbę o wolne" if note.note_type == NoteType.REQUEST else "nieobecność"
    start_date_str = note.start_date.strftime("%Y-%m-%d")
    end_date_str = f" do {note.end_date.strftime('%Y-%m-%d')}" if note.end_date else ""

    message = (
        f"Nowa notatka o niedostępności od {author.first_name} {author.last_name}. "
        f"Typ: {note_type_display}. Okres: {start_date_str}{end_date_str}."
    )

    created_notifications: list[Notification] = []

    for admin_user in admin_users:
        notification = Notification(
            user_id=admin_user.user_id,
            message=message,
            is_read=False,
        )
        db.add(notification)
        db.flush()
        created_notifications.append(notification)
        logger.info(
            "Created admin notification for unavailability note: note_id=%s admin_user_id=%s message=%s",
            note.id,
            admin_user.user_id,
            message,
        )

        # If the admin is currently connected via WebSocket, emit the notification
        try:
            from app.services.socket_broker import get_sio
            from app.services.websocket_manager import chat_ws_manager

            sio = get_sio()
            if sio is not None:
                sids = chat_ws_manager.get_user_sids(admin_user.user_id)
                if sids:
                    payload = {
                        "id": notification.id,
                        "user_id": notification.user_id,
                        "message": notification.message,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.isoformat() if hasattr(notification, "created_at") and notification.created_at else None,
                    }
                    for sid in sids:
                        try:
                            sio.start_background_task(sio.emit, "notification", payload, room=sid)
                            logger.debug("Emitted live notification to sid %s for admin %s", sid, admin_user.user_id)
                        except Exception as e:
                            logger.exception("Failed to emit live notification to sid %s: %s", sid, e)
        except Exception:
            logger.exception("Error while attempting to emit live notification for admin_user_id=%s", admin_user.user_id)

    logger.info(
        "Finished creating admin notifications for unavailability note: note_id=%s admin_count=%s",
        note.id,
        len(admin_users),
    )

    return created_notifications


def get_admin_users_for_notifications(db: Session, note_id: int | None = None) -> list[User]:
    """Pobiera użytkowników z rolą admin do wysyłki powiadomień."""
    admin_role = db.query(Role).filter(Role.name.ilike("admin")).first()
    if not admin_role:
        if note_id is not None:
            logger.warning(
                "Admin role not found while resolving notification recipients: note_id=%s",
                note_id,
            )
        return []

    from app.models.model_role_for_user import RolesForUser

    return (
        db.query(User)
        .join(RolesForUser, User.user_id == RolesForUser.user_id)
        .filter(RolesForUser.role_id == admin_role.id)
        .all()
    )


def build_unavailability_note_notification_message(author: User, note: UnavailabilityNote) -> str:
    """Buduje spójną treść powiadomienia o nowej notatce."""
    note_type_display = "prośbę o wolne" if note.note_type == NoteType.REQUEST else "nieobecność"
    start_date_str = note.start_date.strftime("%Y-%m-%d")
    end_date_str = f" do {note.end_date.strftime('%Y-%m-%d')}" if note.end_date else ""

    return (
        f"Nowa notatka o niedostępności od {author.first_name} {author.last_name}. "
        f"Typ: {note_type_display}. Okres: {start_date_str}{end_date_str}."
    )


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
