from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_constraint_for_optional_element import RaplaConstraintForOptionalElement
from app.models.rapla.model_rapla_constraint import RaplaConstraint
from app.models.rapla.model_rapla_optional_element import RaplaOptionalElement


def get_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaConstraintForOptionalElement]:
    return db.query(RaplaConstraintForOptionalElement).filter(RaplaConstraintForOptionalElement.id == rel_id).first()


def get_relation(db: Session, optional_element_id: int, constraint_id: int) -> Optional[RaplaConstraintForOptionalElement]:
    return db.query(RaplaConstraintForOptionalElement).filter(
        RaplaConstraintForOptionalElement.optional_element_id == optional_element_id,
        RaplaConstraintForOptionalElement.constraint_id == constraint_id,
    ).first()


def list_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaConstraintForOptionalElement]:
    q = db.query(RaplaConstraintForOptionalElement).order_by(RaplaConstraintForOptionalElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_relations_for_optional_element(db: Session, optional_element_id: int, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaConstraintForOptionalElement]:
    q = db.query(RaplaConstraintForOptionalElement).filter(
        RaplaConstraintForOptionalElement.optional_element_id == optional_element_id
    ).order_by(RaplaConstraintForOptionalElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def get_relation_for_optional_element(db: Session, optional_element_id: int) -> Optional[RaplaConstraintForOptionalElement]:
    """Return the first RaplaConstraintForOptionalElement for given optional_element_id, or None."""
    return (
        db.query(RaplaConstraintForOptionalElement)
        .filter(RaplaConstraintForOptionalElement.optional_element_id == optional_element_id)
        .order_by(RaplaConstraintForOptionalElement.id.asc())
        .first()
    )


def list_constraints_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaConstraint]:
    return db.query(RaplaConstraint).join(
        RaplaConstraintForOptionalElement,
        RaplaConstraint.id == RaplaConstraintForOptionalElement.constraint_id,
    ).filter(RaplaConstraintForOptionalElement.optional_element_id == optional_element_id).all()


def get_relations_for_optional_element(db: Session, optional_element_id: int) -> List[RaplaConstraintForOptionalElement]:
    """Return all RaplaConstraintForOptionalElement rows for the given optional_element_id."""
    return (
        db.query(RaplaConstraintForOptionalElement)
        .filter(RaplaConstraintForOptionalElement.optional_element_id == optional_element_id)
        .order_by(RaplaConstraintForOptionalElement.id.asc())
        .all()
    )


def list_optional_elements_for_constraint(db: Session, constraint_id: int) -> List[RaplaOptionalElement]:
    return db.query(RaplaOptionalElement).join(
        RaplaConstraintForOptionalElement,
        RaplaOptionalElement.id == RaplaConstraintForOptionalElement.optional_element_id,
    ).filter(RaplaConstraintForOptionalElement.constraint_id == constraint_id).all()


def add_constraint_to_optional_element(db: Session, optional_element_id: int, constraint_id: int) -> RaplaConstraintForOptionalElement:
    existing = get_relation(db, optional_element_id, constraint_id)
    if existing:
        return existing

    rel = RaplaConstraintForOptionalElement(optional_element_id=optional_element_id, constraint_id=constraint_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_constraint_from_optional_element(db: Session, optional_element_id: int, constraint_id: int) -> None:
    row = get_relation(db, optional_element_id, constraint_id)
    if row:
        db.delete(row)
        db.commit()


def remove_constraint_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
