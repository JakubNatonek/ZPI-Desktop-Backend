from sqlalchemy.orm import Session

from app.cruds.crud_special_equipment import get_or_create_special_equipment


SPECIAL_EQUIPMENT_NAMES = [
    "Projektor",
    "Ekran",
    "Nagłośnienie",
    "Tablica interaktywna",
    "Komputer",
    "Mikrofon",
    "Klimatyzacja",
    "Flipchart",
]


def seed_special_equipment(db: Session) -> None:
    ensured_count = 0
    for equipment_name in SPECIAL_EQUIPMENT_NAMES:
        equipment = get_or_create_special_equipment(db, equipment_name)
        if equipment.id is not None:
            ensured_count += 1

    db.commit()
    print(f"Special equipment seeded. Total ensured: {ensured_count}")