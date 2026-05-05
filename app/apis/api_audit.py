from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.model_user import User
from app.schemas.audit_log import AuditLogResponse, AcknowledgeRequest
from app.cruds import crud_audit

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=Dict[str, Any], dependencies=[Depends(require_role(["admin", "rapla_editor"]))])
def get_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs_data = crud_audit.get_audit_logs(db)
    
    response_logs = []
    for log, user in logs_data:
        mod_name = None
        if user:
            mod_name = f"{user.first_name} {user.last_name}"
            
        response_logs.append(AuditLogResponse(
            id=log.id,
            entity_name=log.entity_name,
            entity_id=log.entity_id,
            action=log.action,
            old_values=log.old_values,
            new_values=log.new_values,
            modified_by=log.modified_by,
            modified_by_name=mod_name,
            timestamp=log.timestamp
        ))
        
    return {
        "last_changes_viewed_at": current_user.last_changes_viewed_at,
        "logs": response_logs
    }

@router.post("/acknowledge", dependencies=[Depends(require_role(["admin", "rapla_editor"]))])
def acknowledge_changes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud_audit.acknowledge_changes(db, current_user.user_id)
    return {"message": "Ack success"}