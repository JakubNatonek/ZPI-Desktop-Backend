from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.model_audit_log import AuditLog, AuditLogView
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.schemas.audit_log import AuditLogDto, AuditLogResponseDto

# Roles whose changes should appear in the audit log view
_PLAN_ROLES = {"admin", "rapla_editor", "wykladowca_rapla_editor"}


def get_all_logs(db: Session) -> list[AuditLog]:
    """Return only logs created by admins or rapla_editors."""
    plan_role_ids = (
        db.query(Role.id)
        .filter(Role.name.in_(_PLAN_ROLES))
        .subquery()
    )
    plan_user_ids = (
        db.query(RolesForUser.user_id)
        .filter(RolesForUser.role_id.in_(plan_role_ids))
        .subquery()
    )
    return (
        db.query(AuditLog)
        .filter(AuditLog.modified_by.in_(plan_user_ids))
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


def get_audit_log_response(db: Session, user_id: int) -> AuditLogResponseDto:
    view = db.query(AuditLogView).filter(AuditLogView.user_id == user_id).first()
    last_viewed_at = view.last_viewed_at if view else None

    logs = get_all_logs(db)
    dtos = [AuditLogDto.model_validate(log) for log in logs]

    return AuditLogResponseDto(last_changes_viewed_at=last_viewed_at, logs=dtos)


def acknowledge_audit_logs(db: Session, user_id: int) -> None:
    now = datetime.now(timezone.utc)
    view = db.query(AuditLogView).filter(AuditLogView.user_id == user_id).first()
    if view:
        view.last_viewed_at = now
    else:
        db.add(AuditLogView(user_id=user_id, last_viewed_at=now))
    db.commit()


def create_audit_log(
    db: Session,
    entity_name: str,
    entity_id: int,
    action: str,
    modified_by: int,
    modified_by_name: str,
    old_values: dict | None = None,
    new_values: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        entity_name=entity_name,
        entity_id=entity_id,
        action=action,
        modified_by=modified_by,
        modified_by_name=modified_by_name,
        old_values=old_values,
        new_values=new_values,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
