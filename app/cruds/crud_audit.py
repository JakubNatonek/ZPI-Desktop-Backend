from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Optional
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
    audit_entry = AuditLog(
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        old_values=old_values,
        new_values=new_values,
        modified_by=user_id,
        timestamp=datetime.utcnow()
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
        user.last_changes_viewed_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user
