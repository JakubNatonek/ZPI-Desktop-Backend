from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_data_type_for_optional_element import RaplaDataTypeForOptionalElement
from app.models.rapla.model_rapla_data_type import RaplaDataType


def get_data_type_for_optional_element_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaDataTypeForOptionalElement]:
    return db.query(RaplaDataTypeForOptionalElement).filter(RaplaDataTypeForOptionalElement.id == rel_id).first()


def get_data_type_for_optional_element(db: Session, optional_element_id: int) -> Optional[RaplaDataType]:
    return db.query(RaplaDataType).join(
        RaplaDataTypeForOptionalElement,
        RaplaDataType.id == RaplaDataTypeForOptionalElement.data_type_id,
    ).filter(RaplaDataTypeForOptionalElement.optional_element_id == optional_element_id).first()


def get_data_type_relation_for_optional_element(db: Session, optional_element_id: int) -> Optional[RaplaDataTypeForOptionalElement]:
    """Return the first RaplaDataTypeForOptionalElement relation for given optional_element_id, or None."""
    return (
        db.query(RaplaDataTypeForOptionalElement)
        .filter(RaplaDataTypeForOptionalElement.optional_element_id == optional_element_id)
        .order_by(RaplaDataTypeForOptionalElement.id.asc())
        .first()
    )


def add_data_type_to_optional_element(db: Session, optional_element_id: int, data_type_id: int) -> RaplaDataTypeForOptionalElement:
    # check if the (optional_element_id, data_type_id) relation already exists
    existing = get_data_type_relation_for_optional_element(db, optional_element_id)
    if existing:
        return existing

    rel = RaplaDataTypeForOptionalElement(optional_element_id=optional_element_id, data_type_id=data_type_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_data_type_from_optional_element(db: Session, optional_element_id: int) -> None:
    # find relation by element+data_type
    row = get_data_type_relation_for_optional_element(db, optional_element_id)
    if row:
        db.delete(row)
        db.commit()


def remove_data_type_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_data_type_for_optional_element_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
        