from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_room_type import create_room_type


class RoomTypeEnum(PyEnum):
    LAB = ("Laboratoryjna", "Lab")
    CWI = ("Ćwiczeniowa", "Cwi")
    WYK = ("Wykładowa", "Wyk")
    PRO = ("Projektowa", "Pro")
    HAL = ("Hala Sportowa", "Hal")
    BOI = ("Boisko", "Boi")


def seed_room_types(db: Session) -> None:
    for rt in RoomTypeEnum:
        type_name, abbreviation = rt.value
        try:
            create_room_type(db, type_name, abbreviation)
        except Exception:
            # ignore errors (e.g., already exists)
            continue

    print("Room types seeded.")