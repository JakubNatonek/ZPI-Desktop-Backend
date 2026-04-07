from typing import Optional
from sqlalchemy.orm import Session

from app.models.model_room_type import RoomType


##
# @brief Return all room types ordered by id.
# @param db Active database session.
# @return List of room type rows.
def get_all_room_types(db: Session) -> list[RoomType]:
    return db.query(RoomType).order_by(RoomType.id.asc()).all()


##
# @brief Find a room type by primary key.
# @param db Active database session.
# @param room_type_id Room type identifier.
# @return Matching row or None when not found.
def get_room_type_by_id(db: Session, room_type_id: int) -> Optional[RoomType]:
    return db.query(RoomType).filter(RoomType.id == room_type_id).first()


##
# @brief Create a room type row.
# @param db Active database session.
# @param type Room type name.
# @param abbreviation Short abbreviation.
# @return Newly created room type row.
def create_room_type(db: Session, type: str, abbreviation: str) -> RoomType:
    room_type = RoomType(type=type, abbreviation=abbreviation)
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


##
# @brief Update an existing room type.
# @param db Active database session.
# @param room_type_id Room type identifier.
# @param type Optional new type name.
# @param abbreviation Optional new abbreviation.
# @return Updated row or None when not found.
def update_room_type(db: Session, room_type_id: int, type: Optional[str] = None, abbreviation: Optional[str] = None) -> Optional[RoomType]:
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        return None

    if type is not None:
        room_type.type = type # type: ignore
    if abbreviation is not None:
        room_type.abbreviation = abbreviation # type: ignore

    db.commit()
    db.refresh(room_type)
    return room_type


##
# @brief Delete a room type by primary key.
# @param db Active database session.
# @param room_type_id Room type identifier.
# @return True if deleted, False when no row was found.
def delete_room_type(db: Session, room_type_id: int) -> bool:
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        return False

    db.delete(room_type)
    db.commit()
    return True
