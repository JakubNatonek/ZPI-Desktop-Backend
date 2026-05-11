from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.model_audit_log import AuditLog
from app.models.model_user import User

def log_change(
    db: Session,
    entity_name: str,
    entity_id: int,
    action: str,
    old_values: Optional[Dict[str, Any]],
    new_values: Optional[Dict[str, Any]],
    user_id: Optional[int]
):
    encoded_old_values = jsonable_encoder(old_values) if old_values is not None else None
    encoded_new_values = jsonable_encoder(new_values) if new_values is not None else None

    audit_entry = AuditLog(
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        old_values=encoded_old_values,
        new_values=encoded_new_values,
        modified_by=user_id,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry

def get_audit_logs(db: Session):
    return db.query(AuditLog, User).outerjoin(User, AuditLog.modified_by == User.user_id).order_by(AuditLog.timestamp.desc()).all()

def acknowledge_changes(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        cast(Any, user).last_changes_viewed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    return user
