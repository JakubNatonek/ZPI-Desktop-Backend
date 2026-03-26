from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_language_name_for_optional_element import RaplaLanguageNameForOptionalElement
from app.models.rapla.model_rapla_language_name import RaplaLanguageName
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement


def get_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaLanguageNameForOptionalElement]:
    return db.query(RaplaLanguageNameForOptionalElement).filter(RaplaLanguageNameForOptionalElement.id == rel_id).first()


def get_relation(db: Session, optional_element_id: int, language_name_id: int) -> Optional[RaplaLanguageNameForOptionalElement]:
    return db.query(RaplaLanguageNameForOptionalElement).filter(
        RaplaLanguageNameForOptionalElement.optional_element_id == optional_element_id,
        RaplaLanguageNameForOptionalElement.language_name_id == language_name_id,
    ).first()


def list_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaLanguageNameForOptionalElement]:
    q = db.query(RaplaLanguageNameForOptionalElement).order_by(RaplaLanguageNameForOptionalElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_language_names_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaLanguageName]:
    return db.query(RaplaLanguageName).join(
        RaplaLanguageNameForOptionalElement,
        RaplaLanguageName.id == RaplaLanguageNameForOptionalElement.language_name_id,
    ).filter(RaplaLanguageNameForOptionalElement.optional_element_id == optional_element_id).all()


def get_list_relations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaLanguageNameForOptionalElement]:
    q = db.query(RaplaLanguageNameForOptionalElement).filter(
        RaplaLanguageNameForOptionalElement.optional_element_id == optional_element_id
    ).order_by(RaplaLanguageNameForOptionalElement.id.asc())

    return q.all()


def list_optional_elements_for_language_name(db: Session, language_name_id: int) -> List[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).join(
        RaplaLanguageNameForOptionalElement,
        RaplaOptionalElement.id == RaplaLanguageNameForOptionalElement.optional_element_id,
    ).filter(RaplaLanguageNameForOptionalElement.language_name_id == language_name_id).all()


def add_language_name_to_optional_element(db: Session, optional_element_id: int, language_name_id: int) -> RaplaLanguageNameForOptionalElement:
    existing = get_relation(db, optional_element_id, language_name_id)
    if existing:
        return existing

    rel = RaplaLanguageNameForOptionalElement(optional_element_id=optional_element_id, language_name_id=language_name_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_language_name_from_optional_element(db: Session, optional_element_id: int, language_name_id: int) -> None:
    row = get_relation(db, optional_element_id, language_name_id)
    if row:
        db.delete(row)
        db.commit()

def remove_language_name_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
