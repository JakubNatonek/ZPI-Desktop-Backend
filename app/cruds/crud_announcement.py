from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.models.model_announcement import Announcement, AnnouncementSeen
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.models.model_user import User


POLAND_TIMEZONE = ZoneInfo("Europe/Warsaw")


def format_announcement_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(POLAND_TIMEZONE).strftime("%Y-%m-%d %H:%M")


def _resolve_author_name(db: Session, author_id: int | None) -> str:
    """Return display name for the announcement author."""
    if author_id is None:
        return "Dziekanat"

    user = (
        db.query(User)
        .options(joinedload(User.teacher_profile), joinedload(User.roles_for_user))
        .filter(User.user_id == author_id)
        .first()
    )
    if user is None:
        return "Dziekanat"

    role_names = set()
    for rfu in user.roles_for_user:
        role = db.query(Role).filter(Role.id == rfu.role_id).first()
        if role:
            role_names.add(role.name.lower())

    if "admin" in role_names:
        return "Dziekanat"

    title = ""
    if user.teacher_profile and user.teacher_profile.title:
        title = user.teacher_profile.title + " "

    return f"{title}{user.first_name} {user.last_name}"


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
                "created_at": format_announcement_datetime(announcement.created_at),
                "author_id": announcement.author_id,
                "author_name": _resolve_author_name(db, announcement.author_id),
            }
        )
    return items


def create_announcement(
    db: Session,
    author_id: int,
    subject: str,
    content: str,
    created_at: datetime | None = None,
) -> Announcement:
    item = Announcement(
        subject=subject.strip(),
        content=content.strip(),
        author_id=author_id,
    )
    if created_at is not None:
        item.created_at = created_at
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
