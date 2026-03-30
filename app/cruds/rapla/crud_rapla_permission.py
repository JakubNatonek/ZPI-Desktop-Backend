from typing import List, Optional, cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_permission import RaplaPermission
from app.schemas.rapla.schema_rapla_permision import RaplaPermission as RaplaPermissionSchema


def get_permission_by_id(db: Session, permission_id: int) -> Optional[RaplaPermission]:
    return db.query(RaplaPermission).filter(RaplaPermission.id == permission_id).first()


def get_permission_by_group(db: Session, group: str) -> Optional[RaplaPermission]:
    return db.query(RaplaPermission).filter(RaplaPermission.group == group).first()

def get_permission_by_access(db: Session, access: str) -> Optional[RaplaPermission]:
    return (
        db.query(RaplaPermission)
        .filter(RaplaPermission.access == access)
        .first()
    )

def get_permission_by_access_and_group(db: Session, access: str, group: str) -> Optional[RaplaPermission]:
    return (
        db.query(RaplaPermission)
        .filter(RaplaPermission.group == group, RaplaPermission.access == access)
        .first()
    )


def list_permissions(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[RaplaPermission]:
    q = db.query(RaplaPermission).order_by(RaplaPermission.group.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_permission(db: Session, access: str, group: Optional[str] = None) -> RaplaPermission:

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


def get_permission_schema_by_id(db: Session, permission_id: int) -> Optional[RaplaPermissionSchema]:
    p = get_permission_by_id(db, permission_id)
    if p is None:
        return None
    return RaplaPermissionSchema(group=cast(Optional[str], p.group), access=cast(str, p.access or ""))

def get_permission_schema_by_model(db: Session, permission: RaplaPermission) -> Optional[RaplaPermissionSchema]:
    return RaplaPermissionSchema(group=cast(Optional[str], permission.group), access=cast(str, permission.access))

def create_permission_from_schema(db: Session, schema: RaplaPermissionSchema) -> RaplaPermission:
    group = schema.group or ""
    return create_permission(db, access=schema.access, group=group)


def update_permission_from_schema(db: Session, permission_id: int, schema: RaplaPermissionSchema) -> RaplaPermission:
    return update_permission(db, permission_id, access=schema.access or None, group=schema.group or None)
