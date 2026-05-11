from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_audit_logs import get_audit_log_response, acknowledge_audit_logs
from app.models.model_user import User
from app.schemas.audit_log import AuditLogResponseDto

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=AuditLogResponseDto, summary="Pobierz logi audytu")
def get_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuditLogResponseDto:
    return get_audit_log_response(db, current_user.user_id)


@router.post("/acknowledge", summary="Zaznacz logi jako przejrzane")
def acknowledge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    acknowledge_audit_logs(db, current_user.user_id)
    return {"message": "ok"}
