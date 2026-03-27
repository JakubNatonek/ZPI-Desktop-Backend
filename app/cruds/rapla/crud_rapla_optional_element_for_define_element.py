from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.rapla.model_rapla_optional_element_for_define_element import (
    RaplaOptionalElementForDefineElement as RaplaOptionalElementForDefineElementModel,
)
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement as RaplaOptionalElementModel
from app.models.rapla.model_rapla_define_element import RaplaDefineElement as RaplaDefineElementModel


def get_relation_by_id(db: Session, relation_id: int) -> Optional[RaplaOptionalElementForDefineElementModel]:
    return db.query(RaplaOptionalElementForDefineElementModel).filter(RaplaOptionalElementForDefineElementModel.id == relation_id).first()


def get_relation(db: Session, optional_element_id: int, define_element_id: int) -> Optional[RaplaOptionalElementForDefineElementModel]:
    return (
        db.query(RaplaOptionalElementForDefineElementModel)
        .filter(
            RaplaOptionalElementForDefineElementModel.optional_element_id == optional_element_id,
            RaplaOptionalElementForDefineElementModel.define_element_id == define_element_id,
        )
        .first()
    )


def list_relations(db: Session, skip: int = 0, limit: int = 100) -> List[RaplaOptionalElementForDefineElementModel]:
    return db.query(RaplaOptionalElementForDefineElementModel).offset(skip).limit(limit).all()


def list_relations_for_define_element(db: Session, define_element_id: int) -> List[RaplaOptionalElementForDefineElementModel]:
    return (
        db.query(RaplaOptionalElementForDefineElementModel)
        .filter(RaplaOptionalElementForDefineElementModel.define_element_id == define_element_id)
        .all()
    )


def list_relations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaOptionalElementForDefineElementModel]:
    return (
        db.query(RaplaOptionalElementForDefineElementModel)
        .filter(RaplaOptionalElementForDefineElementModel.optional_element_id == optional_element_id)
        .all()
    )


def add_relation(db: Session, optional_element_id: int, define_element_id: int) -> RaplaOptionalElementForDefineElementModel:
    # Return existing relation if present
    existing = get_relation(db, optional_element_id=optional_element_id, define_element_id=define_element_id)
    if existing:
        return existing

    # Verify referenced rows exist
    if not db.query(RaplaOptionalElementModel).filter(RaplaOptionalElementModel.id == optional_element_id).first():
        raise ValueError(f"RaplaOptionalElement id={optional_element_id} does not exist")
    if not db.query(RaplaDefineElementModel).filter(RaplaDefineElementModel.id == define_element_id).first():
        raise ValueError(f"RaplaDefineElement id={define_element_id} does not exist")

    db_obj = RaplaOptionalElementForDefineElementModel(optional_element_id=optional_element_id, define_element_id=define_element_id)
    db.add(db_obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return get_relation(db, optional_element_id=optional_element_id, define_element_id=define_element_id)
    db.refresh(db_obj)
    return db_obj


def remove_relation_by_id(db: Session, relation_id: int) -> None:
    obj = get_relation_by_id(db, relation_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()


def remove_relation(db: Session, optional_element_id: int, define_element_id: int) -> None:
    obj = get_relation(db, optional_element_id=optional_element_id, define_element_id=define_element_id)
    if not obj:
        return
    db.delete(obj)
    db.commit()
