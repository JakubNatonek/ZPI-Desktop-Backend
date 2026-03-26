from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_laguage_name_for_define_element import RaplaLanguageNameForDefineElement
from app.models.rapla.model_rapla_language_name import RaplaLanguageName
from app.models.rapla.model_rapla_define_element import RaplaDefineElement


def get_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaLanguageNameForDefineElement]:
    return db.query(RaplaLanguageNameForDefineElement).filter(RaplaLanguageNameForDefineElement.id == rel_id).first()


def get_relation(db: Session, define_element_id: int, language_name_id: int) -> Optional[RaplaLanguageNameForDefineElement]:
    return db.query(RaplaLanguageNameForDefineElement).filter(
        RaplaLanguageNameForDefineElement.define_element_id == define_element_id,
        RaplaLanguageNameForDefineElement.language_name_id == language_name_id,
    ).first()


def list_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaLanguageNameForDefineElement]:
    q = db.query(RaplaLanguageNameForDefineElement).order_by(RaplaLanguageNameForDefineElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_language_names_for_define_element(db: Session, define_element_id: int) -> List[RaplaLanguageName]:
    return db.query(RaplaLanguageName).join(
        RaplaLanguageNameForDefineElement,
        RaplaLanguageName.id == RaplaLanguageNameForDefineElement.language_name_id,
    ).filter(RaplaLanguageNameForDefineElement.define_element_id == define_element_id).all()


def list_define_elements_for_language_name(db: Session, language_name_id: int) -> List[RaplaDefineElement]:
    return db.query(RaplaDefineElement).join(
        RaplaLanguageNameForDefineElement,
        RaplaDefineElement.id == RaplaLanguageNameForDefineElement.define_element_id,
    ).filter(RaplaLanguageNameForDefineElement.language_name_id == language_name_id).all()


def list_relations_for_define_element(db: Session, define_element_id: int) -> List[RaplaLanguageNameForDefineElement]:
    q = db.query(RaplaLanguageNameForDefineElement).filter(
        RaplaLanguageNameForDefineElement.define_element_id == define_element_id
    ).order_by(RaplaLanguageNameForDefineElement.id.asc())

    return q.all()


def add_language_name_to_define_element(db: Session, define_element_id: int, language_name_id: int) -> RaplaLanguageNameForDefineElement:
    existing = get_relation(db, define_element_id, language_name_id)
    if existing:
        return existing

    rel = RaplaLanguageNameForDefineElement(define_element_id=define_element_id, language_name_id=language_name_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_language_name_from_define_element(db: Session, define_element_id: int, language_name_id: int) -> None:
    row = get_relation(db, define_element_id, language_name_id)
    if row:
        db.delete(row)
        db.commit()


def remove_language_name_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
