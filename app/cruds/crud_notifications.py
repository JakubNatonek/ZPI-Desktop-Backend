from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.model_notification import Notification


def get_unread_notifications_for_user(db: Session, user_id: int) -> list[Notification]:
    """Pobiera wszystkie nieprzeczytane powiadomienia użytkownika."""
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_all_notifications_for_user(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Notification], int]:
    """
    Pobiera powiadomienia użytkownika z paginacją.
    Zwraca tuple: (lista powiadomień, całkowita liczba)
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    total_count = query.count()

    notifications = (
        query
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return notifications, total_count


def get_notification_by_id(db: Session, notification_id: int) -> Notification | None:
    """Pobiera powiadomienie po ID."""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def mark_notification_as_read(db: Session, notification_id: int) -> Notification | None:
    """Oznacza powiadomienie jako przeczytane."""
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None

    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """Oznacza wszystkie powiadomienia użytkownika jako przeczytane. Zwraca liczbę zaktualizowanych."""
    unread_notifications = get_unread_notifications_for_user(db, user_id)
    count = len(unread_notifications)

    for notification in unread_notifications:
        notification.is_read = True
        db.add(notification)

    db.commit()
    return count


def create_notification(db: Session, user_id: int, message: str) -> Notification:
    """Tworzy nowe powiadomienie dla użytkownika."""
    notification = Notification(
        user_id=user_id,
        message=message,
        is_read=False,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def count_unread_notifications(db: Session, user_id: int) -> int:
    """Zwraca liczbę nieprzeczytanych powiadomień użytkownika."""
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        .count()
    )


def delete_notification(db: Session, notification_id: int) -> bool:
    """Usuwa powiadomienie. Zwraca True jeśli było, False jeśli nie znaleziono."""
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return False

    db.delete(notification)
    db.commit()
    return True
