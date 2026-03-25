from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.model_announcement import Announcement, AnnouncementSeen


def list_announcements_for_user(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(Announcement, AnnouncementSeen)
        .outerjoin(
            AnnouncementSeen,
            and_(
                AnnouncementSeen.announcement_id == Announcement.id,
                AnnouncementSeen.user_id == user_id,
            ),
        )
        .order_by(Announcement.created_at.desc())
        .all()
    )

    items: list[dict] = []
    for announcement, seen_entry in rows:
        items.append(
            {
                "id": announcement.id,
                "subject": announcement.subject,
                "content": announcement.content,
                "seen": seen_entry is not None,
                "created_at": announcement.created_at,
                "author_id": announcement.author_id,
            }
        )
    return items


def create_announcement(db: Session, author_id: int, subject: str, content: str) -> Announcement:
    item = Announcement(
        subject=subject.strip(),
        content=content.strip(),
        author_id=author_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def mark_announcement_seen(db: Session, announcement_id: int, user_id: int) -> bool:
    announcement_exists = db.query(Announcement.id).filter(Announcement.id == announcement_id).first()
    if announcement_exists is None:
        return False

    existing = (
        db.query(AnnouncementSeen)
        .filter(
            AnnouncementSeen.announcement_id == announcement_id,
            AnnouncementSeen.user_id == user_id,
        )
        .first()
    )
    if existing is not None:
        return True

    db.add(
        AnnouncementSeen(
            announcement_id=announcement_id,
            user_id=user_id,
            seen_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    return True
