from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.room.crud_room_type import get_or_create_room_type


class RoomTypeEnum(PyEnum):
    LAB = ("Laboratoryjna", "Lab")
    CWI = ("Ćwiczeniowa", "Cwi")
    WYK = ("Wykładowa", "Wyk")
    PRO = ("Projektowa", "Pro")
    HAL = ("Hala Sportowa", "Hal")
    BOI = ("Boisko", "Boi")


def seed_room_types(db: Session) -> None:
    for rt in RoomTypeEnum:
        room_type_name, abbreviation = rt.value
        get_or_create_room_type(db, room_type_name, abbreviation)

    print("Room types seeded.")