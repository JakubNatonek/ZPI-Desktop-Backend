from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_data_type import RaplaDataType


def get_data_type_by_id(db: Session, data_type_id: int) -> Optional[RaplaDataType]:
    return db.query(RaplaDataType).filter(RaplaDataType.id == data_type_id).first()


def get_data_type_by_type(db: Session, type_name: str) -> Optional[RaplaDataType]:
    return db.query(RaplaDataType).filter(RaplaDataType.type == type_name).first()


def list_data_types(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaDataType]:
    q = db.query(RaplaDataType).order_by(RaplaDataType.type.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_data_type(db: Session, type_name: str) -> RaplaDataType:
    existing = get_data_type_by_type(db, type_name)
    if existing:
        return existing

    dt = RaplaDataType(type=type_name)
    db.add(dt)
    db.commit()
    db.refresh(dt)
    return dt


def update_data_type(db: Session, id: int, type_name: Optional[str] = None) -> RaplaDataType:
    dt = get_data_type_by_id(db, id)
    if dt is None:
        raise ValueError(f"DataType with id={id} not found")

    if type_name is not None:
        dt.type = type_name

    db.add(dt)
    db.commit()
    db.refresh(dt)
    return dt


def delete_data_type(db: Session, data_type: RaplaDataType) -> None:
    db.delete(data_type)
    db.commit()
