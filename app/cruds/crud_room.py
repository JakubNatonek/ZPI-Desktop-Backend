from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status

from app.cruds.crud_activity import get_activities_by_ids
from app.cruds.crud_room_type import get_room_type_by_id
from app.models.model_room import Room
from app.schemas.room import RoomCreate, RoomUpdate

# NOTE: Why do you chenge data 
def _resolve_building(room_number: str) -> str:
    cleaned = room_number.strip()
    if "-" in cleaned:
        prefix = cleaned.split("-", maxsplit=1)[0].strip()
        if prefix:
            return prefix.upper()

    if cleaned and cleaned[0].isalpha():
        return cleaned[0].upper()

    return "A"

def _resolve_activities(db: Session, activity_ids: list[int]) -> list:
    unique_ids = list(dict.fromkeys(activity_ids))
    resolved_activities = get_activities_by_ids(db, unique_ids)

    found_ids = {activity.id for activity in resolved_activities}
    missing_ids = [activity_id for activity_id in unique_ids if activity_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown activity ids: {missing_ids}",
        )

    return resolved_activities


def _sync_room_id_sequence(db: Session) -> None:
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('room', 'id'), COALESCE((SELECT MAX(id) FROM room), 0) + 1, false)"
        )
    )


def _resolve_room_type(db: Session, room_type_id: int):
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown room type id: {room_type_id}",
        )

    return room_type


def get_rooms(db: Session) -> list[Room]:
    return db.query(Room).options(selectinload(Room.type), selectinload(Room.activities)).order_by(Room.number.asc()).all()


def get_room_by_id(db: Session, room_id: int) -> Optional[Room]:
    return db.query(Room).options(selectinload(Room.type), selectinload(Room.activities)).filter(Room.id == room_id).first()


def get_room_by_number(db: Session, room_number: str) -> Optional[Room]:
    return db.query(Room).options(selectinload(Room.type), selectinload(Room.activities)).filter(Room.number == room_number.strip()).first()

# NOTE/TODO: Chenge building to department maping
def create_room(db: Session, payload: RoomCreate) -> Room:
    _sync_room_id_sequence(db)
    room_number = payload.room_number.strip()
    room = Room(
        building=_resolve_building(room_number),
        number=room_number,
        seats=payload.seats_count,
        type=_resolve_room_type(db, payload.room_type_id),
        description=payload.special_equipment.strip() or None,
    )
    room.activities = _resolve_activities(db, payload.activities)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

# NOTE/TODO: Chenge building to department maping
def update_room(db: Session, room: Room, payload: RoomUpdate) -> Room:
    room_number = payload.room_number.strip()
    room.building = _resolve_building(room_number)
    room.number = room_number
    room.seats = payload.seats_count
    room.type = _resolve_room_type(db, payload.room_type_id)
    room.description = payload.special_equipment.strip() or None
    room.activities = _resolve_activities(db, payload.activities)

    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()

# NOTE: Why do you create JSON by hand when you could use response class??
def map_room_to_response(room: Room) -> dict:
    return {
        "id": room.id,
        "building": room.building,
        "room_number": room.number,
        "seats_count": room.seats,
        "room_type": room.type.type if room.type else "inna",
        "special_equipment": room.description or "",
        "activities": [activity.id for activity in room.activities],
    }
