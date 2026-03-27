from typing import Optional, cast, List

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_data_type import RaplaDataType
from app.schemas.rapla.schema_rapla_data_type import RaplaDataType as RaplaDataTypeSchema


def get_data_type_by_id(db: Session, data_type_id: int) -> Optional[RaplaDataType]:
    return db.query(RaplaDataType).filter(RaplaDataType.id == data_type_id).first()

def get_all_data_type_by_id(db: Session, data_type_id: int) -> List[RaplaDataType]:
    return db.query(RaplaDataType).filter(RaplaDataType.id == data_type_id).all()

def get_data_type_by_type(db: Session, type_name: str) -> Optional[RaplaDataType]:
    return db.query(RaplaDataType).filter(RaplaDataType.type == type_name).first()



def create_data_type(db: Session, type_name: str) -> RaplaDataType:
    existing = get_data_type_by_type(db, type_name)
    if existing:
        return existing

    dt = RaplaDataType(type=type_name)
    db.add(dt)
    db.commit()
    db.refresh(dt)
    return dt


def delete_data_type(db: Session, data_type: RaplaDataType) -> None:
    db.delete(data_type)
    db.commit()


def get_data_type_schema_by_id(db: Session, data_type_id: int) -> Optional[RaplaDataTypeSchema]:
    dt = get_data_type_by_id(db, data_type_id)
    if dt is None:
        return None
    return RaplaDataTypeSchema(type = cast( str, dt.type ) )