from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
from app.cruds.crud_teaching_load import (
    get_teaching_loads,
    get_teaching_load_by_id,
    create_teaching_load,
    patch_teaching_load,
    delete_teaching_load,
    map_teaching_load_to_response,
)

from app.models.model_user import User
from app.schemas.teaching_load import (
    TeachingLoadAssignmentDto,
    TeachingLoadCreatePayload,
    TeachingLoadPatchPayload,
    TeachingLoadListResponse,
)

router = APIRouter(prefix="/teaching-loads", tags=["teaching-loads"])


def _require_admin(current_user: User) -> None:
    if not user_has_role(current_user, "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wymagana rola: admin")


@router.get("/list", response_model=TeachingLoadListResponse, summary="Lista przydziałów godzin")
def list_teaching_loads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingLoadListResponse:
    _require_admin(current_user)
    items = [map_teaching_load_to_response(item) for item in get_teaching_loads(db)]
    return TeachingLoadListResponse(items=items)


@router.post(
    "",
    response_model=TeachingLoadAssignmentDto,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz przydział godzin",
)
def create_assignment(
    payload: TeachingLoadCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingLoadAssignmentDto:
    _require_admin(current_user)
    result = create_teaching_load(db, payload)
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "TeachingLoadAssignment", result.id, "create",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        new_values=map_teaching_load_to_response(result),
    )
    return map_teaching_load_to_response(result)


@router.patch("/{assignment_id}", response_model=TeachingLoadAssignmentDto, summary="Edytuj przydział godzin")
def update_assignment(
    assignment_id: int,
    payload: TeachingLoadPatchPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeachingLoadAssignmentDto:
    _require_admin(current_user)
    old = get_teaching_load_by_id(db, assignment_id)
    if old is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału")
    result = patch_teaching_load(db, old, payload)
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "TeachingLoadAssignment", assignment_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        old_values=map_teaching_load_to_response(old) if old else None,
        new_values=map_teaching_load_to_response(result),
    )
    return map_teaching_load_to_response(result)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń przydział godzin")
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _require_admin(current_user)
    old = get_teaching_load_by_id(db, assignment_id)
    if old is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału")
    delete_teaching_load(db, old)
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "TeachingLoadAssignment", assignment_id, "delete",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        old_values=map_teaching_load_to_response(old) if old else None,
    )
