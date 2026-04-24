from sqlalchemy.orm import Session
from typing import cast
from datetime import datetime

from app.models.model_room import Room
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.rapla.model_rapla_room_to_resourc import RaplaRoomToResourc
from app.cruds.rapla.crude_rapla_room_type_to_category import get_categories_for_room_type_id
from app.schemas.rapla.resorces.schema_rapla_resourc_room import SchemaRaplaResourcRoom
from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema
from app.cruds.rapla.crud_rapla_department_for_category import get_department_category_by_department_id
from app.cruds.rapla.crud_rapla_permission_for_resourc import get_permission_by_resourc_id
from app.cruds.rapla.crud_rapla_permission import get_permission_schema_by_model
from app.cruds.rapla.rapla_format_datetime import format_rapla_datetime


def list_room_to_resourc_mappings(db: Session) -> list[RaplaRoomToResourc]:
    return db.query(RaplaRoomToResourc).order_by(RaplaRoomToResourc.id.asc()).all()


def get_resorsc_by_room_id(db: Session, room_id: int) -> ModelRaplaResourc | None:
    mapping = (
        db.query(RaplaRoomToResourc)
        .filter(RaplaRoomToResourc.room_id == room_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == mapping.rapla_resourc_id).first()


def get_room_by_resourc_id(db: Session, rapla_resourc_id: int) -> Room | None:
    mapping = (
        db.query(RaplaRoomToResourc)
        .filter(RaplaRoomToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )
    if mapping is None:
        return None

    return db.query(Room).filter(Room.id == mapping.room_id).first()


def get_mapping_by_room_and_resourc(db: Session, room_id: int, rapla_resourc_id: int) -> RaplaRoomToResourc | None:
    return (
        db.query(RaplaRoomToResourc)
        .filter(RaplaRoomToResourc.room_id == room_id)
        .filter(RaplaRoomToResourc.rapla_resourc_id == rapla_resourc_id)
        .first()
    )


def create_room_to_resourc_mapping(db: Session, room_id: int, rapla_resourc_id: int) -> RaplaRoomToResourc:
    existing = get_mapping_by_room_and_resourc(db, room_id, rapla_resourc_id)
    if existing is not None:
        return existing

    mapping = RaplaRoomToResourc(room_id=room_id, rapla_resourc_id=rapla_resourc_id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


def delete_room_to_resourc_mapping(db: Session, room_id: int, rapla_resourc_id: int) -> bool:
    mapping = get_mapping_by_room_and_resourc(db, room_id, rapla_resourc_id)
    if mapping is None:
        return False

    db.delete(mapping)
    db.commit()
    return True


def room_to_resourc_schema(db: Session, room: Room) -> SchemaRaplaResourcRoom | None:
    room_id = cast(int | None, room.id)
    if room_id is None:
        return None

    resource = get_resorsc_by_room_id(db, room_id)
    if resource is None:
        return None

    permission_models = get_permission_by_resourc_id(db, cast(int, resource.id))
    permission_schemas: list[RaplaPermissionSchema] = []
    for permission_model in permission_models:
        permission_schema = get_permission_schema_by_model(db, permission_model)
        if permission_schema is not None:
            permission_schemas.append(permission_schema)

    department_keys: list[str] = []
    for department in room.departments:
        department_category = get_department_category_by_department_id(db, cast(int, department.id))
        key = cast(str | None, getattr(department_category, "key", None))
        if key:
            department_keys.append(key)

    # Preserve order but remove duplicates.
    department_keys = list(dict.fromkeys(department_keys))

    room_type_id = cast(int | None, room.type_id)
    room_type_key: str | None = None
    if room_type_id is not None:
        categories = get_categories_for_room_type_id(db, room_type_id)
        category = categories[0] if categories else None
        if category is not None:
            room_type_key = cast(str, category.key)
    if room_type_key is None and room.room_type is not None:
        room_type_key = cast(str, room.room_type.abbreviation)

    return SchemaRaplaResourcRoom(
        uuid=cast(str, resource.uuid),
        owner=cast(str, resource.owner),
        created_at=format_rapla_datetime(cast(datetime, resource.created_at)),
        last_changed=format_rapla_datetime(cast(datetime, resource.last_changed)),
        last_changed_by=cast(str, resource.last_changed_by),
        room_number=cast(str, room.number),
        seats=cast(int | None, room.seats),
        room_type=room_type_key,
        departments=department_keys,
        permissions=permission_schemas,
    )


def all_room_to_resourc_schema(db: Session) -> list[SchemaRaplaResourcRoom]:
    rooms = db.query(Room).order_by(Room.number.asc()).all()
    schemas: list[SchemaRaplaResourcRoom] = []
    for room in rooms:
        try:
            room_schema = room_to_resourc_schema(db, room)
            if room_schema is not None:
                schemas.append(room_schema)
        except Exception:
            continue

    return schemas
