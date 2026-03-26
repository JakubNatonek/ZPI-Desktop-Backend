from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement


def get_optional_element_by_id(db: Session, element_id: int) -> Optional[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).filter(RaplaOptionalElement.id == element_id).first()


def get_optional_element_by_name(db: Session, name: str) -> Optional[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).filter(RaplaOptionalElement.name == name).first()


def list_optional_elements(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaOptionalElement]:
    q = db.query(RaplaOptionalElement).order_by(RaplaOptionalElement.name.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_optional_element(db: Session, name: str, default_value: Optional[str] = None) -> RaplaOptionalElement:
    existing = get_optional_element_by_name(db, name)
    if existing:
        return existing

    el = RaplaOptionalElement(name=name, default_value=default_value)
    db.add(el)
    db.commit()
    db.refresh(el)
    return el

# WTF IS THIS NEED I HELP
def update_optional_element(db: Session, element: RaplaOptionalElement, **fields) -> RaplaOptionalElement:
    for k, v in fields.items():
        if hasattr(element, k):
            setattr(element, k, v)
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


def delete_optional_element(db: Session, element: RaplaOptionalElement) -> None:
    db.delete(element)
    db.commit()
