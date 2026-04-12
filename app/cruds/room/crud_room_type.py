import re
from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_room_type import RoomType


def get_all_room_types(db: Session) -> list[RoomType]:
    """Return all room types ordered by id."""
    return db.query(RoomType).order_by(RoomType.id.asc()).all()


def get_room_type_by_id(db: Session, room_type_id: int) -> Optional[RoomType]:
    return db.query(RoomType).filter(RoomType.id == room_type_id).first()


def _normalize_room_type_name(room_type_name: str) -> str:
    return room_type_name.strip()


def get_room_type_by_name(db: Session, room_type_name: str) -> Optional[RoomType]:
    """Find a room type by exact name."""
    normalized_name = _normalize_room_type_name(room_type_name)
    return db.query(RoomType).filter(RoomType.type == normalized_name).first()


def _build_room_type_abbreviation(room_type_name: str) -> str:
    normalized_name = _normalize_room_type_name(room_type_name)
    if not normalized_name:
        return "RT"

    words = [part for part in re.split(r"\s+", normalized_name) if part]
    abbreviation = "".join(word[0] for word in words)
    return abbreviation[:10].upper() or "RT"


def create_room_type(db: Session, room_type_name: str, abbreviation: str) -> RoomType:
    """Create a room type row and commit it immediately."""
    normalized_name = _normalize_room_type_name(room_type_name)
    room_type = RoomType(type=normalized_name, abbreviation=abbreviation)
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


def get_or_create_room_type(
    db: Session,
    room_type_name: str,
    abbreviation: Optional[str] = None,
) -> RoomType:
    """Return an existing room type or create and commit a new one."""
    normalized_name = _normalize_room_type_name(room_type_name)
    room_type = get_room_type_by_name(db, normalized_name)
    if room_type is not None:
        return room_type

    room_type = RoomType(
        type=normalized_name,
        abbreviation=abbreviation or _build_room_type_abbreviation(normalized_name),
    )
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


def update_room_type(
    db: Session,
    room_type_id: int,
    room_type_name: Optional[str] = None,
    abbreviation: Optional[str] = None,
) -> Optional[RoomType]:
    """Update an existing room type."""
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        return None

    if room_type_name is not None:
        room_type.type = _normalize_room_type_name(room_type_name)
    if abbreviation is not None:
        room_type.abbreviation = abbreviation

    db.commit()
    db.refresh(room_type)
    return room_type


def delete_room_type(db: Session, room_type_id: int) -> bool:
    """Delete a room type by primary key."""
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        return False

    db.delete(room_type)
    db.commit()
    return True
