from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_permission_for_resourc import RaplaPermissionForResourc
from app.models.rapla.model_rapla_permission import RaplaPermission



def list_permission_for_resourc_mappings(db: Session) -> list[RaplaPermissionForResourc]:
    return db.query(RaplaPermissionForResourc).order_by(RaplaPermissionForResourc.id.asc()).all()


def get_permission_mapping(db: Session, resourc_id: int, permission_id: int) -> RaplaPermissionForResourc | None:
    return (
        db.query(RaplaPermissionForResourc)
        .filter(RaplaPermissionForResourc.resourc_id == resourc_id)
        .filter(RaplaPermissionForResourc.permission_id == permission_id)
        .first()
    )

def get_permission_by_resourc_id(db: Session, resourc_id: int) -> list[RaplaPermission]:
    """Return RaplaPermission rows associated with the given resource id."""
    return (
        db.query(RaplaPermission)
        .join(RaplaPermissionForResourc, RaplaPermission.id == RaplaPermissionForResourc.permission_id)
        .filter(RaplaPermissionForResourc.resourc_id == resourc_id)
        .all()
    )


def create_permission_for_resourc(db: Session, resourc_id: int, permission_id: int) -> RaplaPermissionForResourc:
    existing = get_permission_mapping(db, resourc_id, permission_id)
    if existing is not None:
        return existing

    m = RaplaPermissionForResourc(resourc_id=resourc_id, permission_id=permission_id)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def delete_permission_for_resourc(db: Session, resourc_id: int, permission_id: int) -> bool:
    mapping = get_permission_mapping(db, resourc_id, permission_id)
    if mapping is None:
        return False
    db.delete(mapping)
    db.commit()
    return True
