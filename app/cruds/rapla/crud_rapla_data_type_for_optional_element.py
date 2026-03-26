from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_data_type_for_optional_element import RaplaDataTypeForOptionalElement
from app.models.rapla.model_rapla_data_type import RaplaDataType
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement


def get_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaDataTypeForOptionalElement]:
    return db.query(RaplaDataTypeForOptionalElement).filter(RaplaDataTypeForOptionalElement.id == rel_id).first()


def get_relation(db: Session, optional_element_id: int, data_type_id: int) -> Optional[RaplaDataTypeForOptionalElement]:
    return db.query(RaplaDataTypeForOptionalElement).filter(
        RaplaDataTypeForOptionalElement.optional_element_id == optional_element_id,
        RaplaDataTypeForOptionalElement.data_type_id == data_type_id,
    ).first()


def list_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaDataTypeForOptionalElement]:
    q = db.query(RaplaDataTypeForOptionalElement).order_by(RaplaDataTypeForOptionalElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_data_types_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaDataType]:
    return db.query(RaplaDataType).join(
        RaplaDataTypeForOptionalElement,
        RaplaDataType.id == RaplaDataTypeForOptionalElement.data_type_id,
    ).filter(RaplaDataTypeForOptionalElement.optional_element_id == optional_element_id).all()


def list_relations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaDataTypeForOptionalElement]:
    q = db.query(RaplaDataTypeForOptionalElement).filter(
        RaplaDataTypeForOptionalElement.optional_element_id == optional_element_id
    ).order_by(RaplaDataTypeForOptionalElement.id.asc())

    return q.all()


def list_optional_elements_for_data_type(db: Session, data_type_id: int) -> List[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).join(
        RaplaDataTypeForOptionalElement,
        RaplaOptionalElement.id == RaplaDataTypeForOptionalElement.optional_element_id,
    ).filter(RaplaDataTypeForOptionalElement.data_type_id == data_type_id).all()


def add_data_type_to_optional_element(db: Session, optional_element_id: int, data_type_id: int) -> RaplaDataTypeForOptionalElement:
    existing = get_relation(db, optional_element_id, data_type_id)
    if existing:
        return existing

    rel = RaplaDataTypeForOptionalElement(optional_element_id=optional_element_id, data_type_id=data_type_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_data_type_from_optional_element(db: Session, optional_element_id: int, data_type_id: int) -> None:
    row = get_relation(db, optional_element_id, data_type_id)
    if row:
        db.delete(row)
        db.commit()


def remove_data_type_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
        