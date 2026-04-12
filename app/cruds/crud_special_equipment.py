from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_special_equipment import SpecialEquipment


def get_all_special_equipment(db: Session) -> list[SpecialEquipment]:
    return db.query(SpecialEquipment).order_by(SpecialEquipment.name.asc()).all()


def get_special_equipment_by_id(db: Session, special_equipment_id: int) -> Optional[SpecialEquipment]:
    return db.query(SpecialEquipment).filter(SpecialEquipment.id == special_equipment_id).first()


def get_special_equipment_by_name(db: Session, name: str) -> Optional[SpecialEquipment]:
    cleaned_name = name.strip()
    if not cleaned_name:
        return None

    return db.query(SpecialEquipment).filter(SpecialEquipment.name == cleaned_name).first()


def create_special_equipment(db: Session, name: str) -> SpecialEquipment:
    special_equipment = SpecialEquipment(name=name.strip())
    db.add(special_equipment)
    db.flush()
    return special_equipment


def get_or_create_special_equipment(db: Session, name: str) -> SpecialEquipment:
    special_equipment = get_special_equipment_by_name(db, name)
    if special_equipment is not None:
        return special_equipment

    return create_special_equipment(db, name)


def get_special_equipment_by_ids(db: Session, special_equipment_ids: list[int]) -> list[SpecialEquipment]:
    if not special_equipment_ids:
        return []

    return db.query(SpecialEquipment).filter(SpecialEquipment.id.in_(special_equipment_ids)).all()