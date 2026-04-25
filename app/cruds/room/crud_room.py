from typing import Optional, cast

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from fastapi import HTTPException, status

from app.cruds.crud_activity import get_activities_by_ids
from app.cruds.crud_department import get_departments_by_ids
from app.cruds.crud_special_equipment import get_special_equipment_by_ids
from app.cruds.rapla.crud_rapla_resourc import create_resourc
from app.cruds.rapla.crud_rapla_room_to_resourc import create_room_to_resourc_mapping, get_resorsc_by_room_id
from app.cruds.room.crud_room_type import get_room_type_by_id
from app.models.model_room import Room
from app.schemas.room import RoomCreate, RoomUpdate

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


def _resolve_special_equipment(db: Session, special_equipment_ids: list[int]) -> list:
    unique_ids = list(dict.fromkeys(special_equipment_ids))
    resolved_special_equipment = get_special_equipment_by_ids(db, unique_ids)

    found_ids = {equipment.id for equipment in resolved_special_equipment}
    missing_ids = [equipment_id for equipment_id in unique_ids if equipment_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown special equipment ids: {missing_ids}",
        )

    return resolved_special_equipment


def _resolve_departments(db: Session, department_ids: list[int]) -> list:
    unique_ids = list(dict.fromkeys(department_ids))
    resolved_departments = get_departments_by_ids(db, unique_ids)

    found_ids = {department.id for department in resolved_departments}
    missing_ids = [department_id for department_id in unique_ids if department_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown department ids: {missing_ids}",
        )

    return resolved_departments


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


def _ensure_rapla_resource_mapping_for_room(db: Session, room: Room) -> None:
    if room.id is None:
        raise RuntimeError("Room must be persisted before creating Rapla mapping")

    existing = get_resorsc_by_room_id(db, room.id)
    if existing is not None:
        return

    resource = create_resourc(db)
    create_room_to_resourc_mapping(db, room_id=room.id, rapla_resourc_id=resource.id)


def get_rooms(db: Session) -> list[Room]:
    return db.query(Room).options(
        selectinload(Room.room_type),
        selectinload(Room.departments),
        selectinload(Room.activities),
        selectinload(Room.special_equipment),
    ).order_by(Room.number.asc()).all()


def get_room_by_id(db: Session, room_id: int) -> Optional[Room]:
    return db.query(Room).options(
        selectinload(Room.room_type),
        selectinload(Room.departments),
        selectinload(Room.activities),
        selectinload(Room.special_equipment),
    ).filter(Room.id == room_id).first()


def get_room_by_number(db: Session, room_number: str) -> Optional[Room]:
    return db.query(Room).options(
        selectinload(Room.room_type),
        selectinload(Room.departments),
        selectinload(Room.activities),
        selectinload(Room.special_equipment),
    ).filter(Room.number == room_number.strip()).first()

def create_room(db: Session, payload: RoomCreate) -> Room:
    _sync_room_id_sequence(db)
    room_number = payload.room_number.strip()
    room = Room(
        number=room_number,
        seats=payload.seats_count,
        room_type=_resolve_room_type(db, payload.room_type_id),
    )
    room.departments = _resolve_departments(db, payload.departments)
    room.activities = _resolve_activities(db, payload.activities)
    room.special_equipment = _resolve_special_equipment(db, payload.special_equipment)
    db.add(room)
    db.commit()
    db.refresh(room)

    _ensure_rapla_resource_mapping_for_room(db, room)
    return room


def create_room_for_seed(
    db: Session,
    *,
    room_id: int,
    room_number: str,
    seats_count: int,
    room_type_id: int,
    departments: list[int],
    activities: list[int],
    special_equipment: list[int],
    description: Optional[str] = None,
) -> Room:
    _sync_room_id_sequence(db)

    room = Room(
        id=room_id,
        number=room_number.strip(),
        seats=seats_count,
        description=description,
        room_type=_resolve_room_type(db, room_type_id),
    )
    room.departments = _resolve_departments(db, departments)
    room.activities = _resolve_activities(db, activities)
    room.special_equipment = _resolve_special_equipment(db, special_equipment)

    db.add(room)
    db.commit()
    db.refresh(room)

    _ensure_rapla_resource_mapping_for_room(db, room)
    return room

def update_room(db: Session, room: Room, payload: RoomUpdate) -> Room:
    room_number = payload.room_number.strip()
    room.number = room_number
    room.seats = payload.seats_count
    room.room_type = _resolve_room_type(db, payload.room_type_id)
    room.departments = _resolve_departments(db, payload.departments)
    room.activities = _resolve_activities(db, payload.activities)
    room.special_equipment = _resolve_special_equipment(db, payload.special_equipment)

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
        "room_number": room.number,
        "seats_count": room.seats,
        "room_type_id": room.room_type.id if room.room_type else None,
        "room_type": room.room_type.type if room.room_type else "inna",
        "special_equipment": [equipment.id for equipment in room.special_equipment],
        "special_equipment_names": [equipment.name for equipment in room.special_equipment],
        "activities": [activity.id for activity in room.activities],
        "activity_names": [activity.name for activity in room.activities],
        "departments": [department.id for department in room.departments],
        "department_names": [department.name for department in room.departments],
    }
