from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_permission import RaplaPermission


def get_permission_by_id(db: Session, permission_id: int) -> Optional[RaplaPermission]:
    return db.query(RaplaPermission).filter(RaplaPermission.id == permission_id).first()


def get_permission_by_group(db: Session, group: str) -> Optional[RaplaPermission]:
    return db.query(RaplaPermission).filter(RaplaPermission.group == group).first()


def list_permissions(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaPermission]:
    q = db.query(RaplaPermission).order_by(RaplaPermission.group.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_permission(db: Session, access: str, group: str) -> RaplaPermission:
    existing = get_permission_by_group(db, group)
    if existing:
        return existing

    p = RaplaPermission(access=access, group=group)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_permission(db: Session, id: int, access: str | None = None, group: str | None = None) -> RaplaPermission:
    permission = get_permission_by_id(db, id)
    if permission is None:
        raise ValueError(f"Permission with id={id} not found")

    if access is not None:
        permission.access = access
    if group is not None:
        permission.group = group

    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db: Session, permission: RaplaPermission) -> None:
    db.delete(permission)
    db.commit()


def delete_permission_by_id(db: Session, permission_id: int) -> bool:
    permission = get_permission_by_id(db, permission_id)
    if permission is None:
        return False
    db.delete(permission)
    db.commit()
    return True
