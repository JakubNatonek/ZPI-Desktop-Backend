from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from typing import cast

from sqlalchemy.orm import Session

from app.models.rapla.model_rapla_define_element import RaplaDefineElement


def get_define_element_by_id(db: Session, element_id: int) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.id == element_id).first()


def get_define_element_by_name(db: Session, name: str) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.name == name).first()


def get_define_element_by_uuid(db: Session, uuid: str) -> Optional[RaplaDefineElement]:
    return db.query(RaplaDefineElement).filter(RaplaDefineElement.uuid == uuid).first()


def get_all_define_elements(db: Session,) -> List[RaplaDefineElement]:
    return db.query(RaplaDefineElement).order_by(RaplaDefineElement.name.asc()).all()


def create_define_element(db: Session, 
    name: str, 
    uuid: str | None = None,
    created_at: datetime | None = None,
    last_changed: datetime | None = None,
) -> RaplaDefineElement:
  
    if uuid is not None:
        existing = get_define_element_by_uuid(db, uuid)
        if existing is not None:
            return existing
        
    now = datetime.now(timezone.utc)
    if created_at is None:
        created_at = now
    
    if last_changed is None:
        last_changed = created_at

    if uuid is None:
        uuid = str(uuid4())

    el = RaplaDefineElement(
        name=name, 
        uuid=uuid,
        created_at=created_at,
        last_changed=last_changed,
    )
    db.add(el)
    db.commit()
    db.refresh(el)
    return el




def delete_define_element(db: Session, element: RaplaDefineElement) -> None:
    db.delete(element)
    db.commit()
