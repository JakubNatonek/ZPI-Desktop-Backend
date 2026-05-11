from typing import List, Optional, cast
from datetime import datetime, timezone
from uuid import uuid4


from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.cruds.rapla.crud_rapla_users import get_first_rapla_users_by_username

def get_resourc_by_id(db: Session, id: int) -> Optional[ModelRaplaResourc]:
    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.id == id).first()


def get_resourc_by_uuid(db: Session, uuid: str) -> Optional[ModelRaplaResourc]:
    return db.query(ModelRaplaResourc).filter(ModelRaplaResourc.uuid == uuid).first()


def list_resourcs(db: Session, skip: Optional[int] = None, limit: Optional[int] = None) -> List[ModelRaplaResourc]:
    q = db.query(ModelRaplaResourc).order_by(ModelRaplaResourc.id.asc())
    if skip is not None:
        q = q.offset(skip)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def create_resourc(
    db: Session, 
    owner: str | None = None, 
    uuid: str | None = None, 
    created_at:datetime | None = None, 
    last_changed:datetime | None = None, 
    last_changed_by: str | None = None
) -> ModelRaplaResourc:
    
    if uuid is not None:
        existing = get_resourc_by_uuid(db, uuid)
        if existing is not None:
            return existing
    
    if owner is None:
        system_user = get_first_rapla_users_by_username(db, "system")
        if system_user is None:
            raise ValueError("Missing Rapla 'system' user; cannot infer resource owner")
        owner = cast(str, system_user.uuid)

    if last_changed_by is None:
        last_changed_by = owner

    now = datetime.now(timezone.utc)
    if created_at is None:
        created_at = now
    
    if last_changed is None:
        last_changed = created_at
    
    if uuid is None:
        uuid = str(uuid4())

    r = ModelRaplaResourc(
        uuid=uuid, 
        owner=owner, 
        created_at=created_at, 
        last_changed=last_changed, 
        last_changed_by=last_changed_by
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def delete_resourc(db: Session, resourc: ModelRaplaResourc) -> None:
    db.delete(resourc)
    db.commit()


def delete_resourc_by_id(db: Session, id: int) -> bool:
    r = get_resourc_by_id(db, id)
    if r is None:
        return False
    db.delete(r)
    db.commit()
    return True
