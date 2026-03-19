import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_room import Room
from app.schemas.room import RoomCreate, RoomUpdate


def _resolve_building(room_number: str) -> str:
    cleaned = room_number.strip()
    if "-" in cleaned:
        prefix = cleaned.split("-", maxsplit=1)[0].strip()
        if prefix:
            return prefix.upper()

    if cleaned and cleaned[0].isalpha():
        return cleaned[0].upper()

    return "A"


def _serialize_activities(activities: list[str]) -> str:
    return json.dumps(activities, ensure_ascii=False)


def _deserialize_activities(raw: Optional[str]) -> list[str]:
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    return [item.strip() for item in raw.split(",") if item.strip()]


def get_rooms(db: Session) -> list[Room]:
    return db.query(Room).order_by(Room.number.asc()).all()


def get_room_by_id(db: Session, room_id: int) -> Optional[Room]:
    return db.query(Room).filter(Room.id == room_id).first()


def get_room_by_number(db: Session, room_number: str) -> Optional[Room]:
    return db.query(Room).filter(Room.number == room_number.strip()).first()


def create_room(db: Session, payload: RoomCreate) -> Room:
    room_number = payload.room_number.strip()
    room = Room(
        building=_resolve_building(room_number),
        number=room_number,
        seats=payload.seats_count,
        type=payload.room_type.strip(),
        description=payload.special_equipment.strip() or None,
        activities=_serialize_activities(payload.activities),
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: Room, payload: RoomUpdate) -> Room:
    room_number = payload.room_number.strip()
    room.building = _resolve_building(room_number)
    room.number = room_number
    room.seats = payload.seats_count
    room.type = payload.room_type.strip()
    room.description = payload.special_equipment.strip() or None
    room.activities = _serialize_activities(payload.activities)

    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()


def map_room_to_response(room: Room) -> dict:
    return {
        "id": room.id,
        "building": room.building,
        "room_number": room.number,
        "seats_count": room.seats,
        "room_type": room.type or "inna",
        "special_equipment": room.description or "",
        "activities": _deserialize_activities(room.activities),
    }
