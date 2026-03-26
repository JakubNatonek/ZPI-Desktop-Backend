from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_permission_for_define_element import RaplaPermissionForDefineElement
from app.models.rapla.model_rapla_permission import RaplaPermission
from app.models.rapla.model_rapla_define_element import RaplaDefineElement


def get_relation_by_id(db: Session, rel_id: int) -> Optional[RaplaPermissionForDefineElement]:
    return db.query(RaplaPermissionForDefineElement).filter(RaplaPermissionForDefineElement.id == rel_id).first()


def get_relation(db: Session, define_element_id: int, permission_id: int) -> Optional[RaplaPermissionForDefineElement]:
    return db.query(RaplaPermissionForDefineElement).filter(
        RaplaPermissionForDefineElement.define_element_id == define_element_id,
        RaplaPermissionForDefineElement.permission_id == permission_id,
    ).first()


def list_relations(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaPermissionForDefineElement]:
    q = db.query(RaplaPermissionForDefineElement).order_by(RaplaPermissionForDefineElement.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def list_permissions_for_define_element(db: Session, define_element_id: int) -> List[RaplaPermission]:
    return db.query(RaplaPermission).join(
        RaplaPermissionForDefineElement,
        RaplaPermission.id == RaplaPermissionForDefineElement.permission_id,
    ).filter(RaplaPermissionForDefineElement.define_element_id == define_element_id).all()


def list_define_elements_for_permission(db: Session, permission_id: int) -> List[RaplaDefineElement]:
    return db.query(RaplaDefineElement).join(
        RaplaPermissionForDefineElement,
        RaplaDefineElement.id == RaplaPermissionForDefineElement.define_element_id,
    ).filter(RaplaPermissionForDefineElement.permission_id == permission_id).all()


def list_relations_for_define_element(db: Session, define_element_id: int) -> List[RaplaPermissionForDefineElement]:
    q = db.query(RaplaPermissionForDefineElement).filter(
        RaplaPermissionForDefineElement.define_element_id == define_element_id
    ).order_by(RaplaPermissionForDefineElement.id.asc())

    return q.all()


def add_permission_to_define_element(db: Session, define_element_id: int, permission_id: int) -> RaplaPermissionForDefineElement:
    existing = get_relation(db, define_element_id, permission_id)
    if existing:
        return existing

    rel = RaplaPermissionForDefineElement(define_element_id=define_element_id, permission_id=permission_id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


def remove_permission_from_define_element(db: Session, define_element_id: int, permission_id: int) -> None:
    row = get_relation(db, define_element_id, permission_id)
    if row:
        db.delete(row)
        db.commit()


def remove_permission_relation_by_id(db: Session, rel_id: int) -> None:
    row = get_relation_by_id(db, rel_id)
    if row:
        db.delete(row)
        db.commit()
