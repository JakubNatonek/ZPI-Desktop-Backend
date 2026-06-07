from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.dependencies.auth import require_role
from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
from app.cruds.crud_teaching_loads import (
    get_all_teaching_loads,
    get_teaching_load_by_id,
    create_teaching_load,
    patch_teaching_load,
    delete_teaching_load,
    _build_dto,
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
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> TeachingLoadListResponse:
    items = get_all_teaching_loads(db)
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
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> TeachingLoadAssignmentDto:
    result = create_teaching_load(db, payload)
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "TeachingLoadAssignment", result.id, "create",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        new_values={
            "teacher": f"{result.teacher_title or ''} {result.teacher_first_name} {result.teacher_last_name}".strip(),
            "subject_name": result.subject_name,
            "activity_name": result.activity_name,
            "semester_name": result.semester_name,
            "hours": result.hours,
            "field_of_study_label": result.field_of_study_label,
            "group_label": result.group_label,
        },
    )
    return result


@router.patch("/{assignment_id}", response_model=TeachingLoadAssignmentDto, summary="Edytuj przydział godzin")
def update_assignment(
    assignment_id: int,
    payload: TeachingLoadPatchPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> TeachingLoadAssignmentDto:
    old_orm = get_teaching_load_by_id(db, assignment_id)
    old = _build_dto(old_orm) if old_orm else None
    result = patch_teaching_load(db, assignment_id, payload)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału")
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email

    old_vals: dict = {}
    new_vals: dict = {}
    if old:
        old_teacher = f"{old.teacher_title or ''} {old.teacher_first_name} {old.teacher_last_name}".strip()
        new_teacher = f"{result.teacher_title or ''} {result.teacher_first_name} {result.teacher_last_name}".strip()
        if old_teacher != new_teacher:
            old_vals["teacher"] = old_teacher
            new_vals["teacher"] = new_teacher
        if (old.subject_name or "") != (result.subject_name or ""):
            old_vals["subject_name"] = old.subject_name
            new_vals["subject_name"] = result.subject_name
        if (old.activity_name or "") != (result.activity_name or ""):
            old_vals["activity_name"] = old.activity_name
            new_vals["activity_name"] = result.activity_name
        if (old.semester_name or "") != (result.semester_name or ""):
            old_vals["semester_name"] = old.semester_name
            new_vals["semester_name"] = result.semester_name
        if old.hours != result.hours:
            old_vals["hours"] = old.hours
            new_vals["hours"] = result.hours
        if (old.field_of_study_label or "") != (result.field_of_study_label or ""):
            old_vals["field_of_study_label"] = old.field_of_study_label
            new_vals["field_of_study_label"] = result.field_of_study_label
        if (old.group_label or "") != (result.group_label or ""):
            old_vals["group_label"] = old.group_label
            new_vals["group_label"] = result.group_label

    create_audit_log(
        db, "TeachingLoadAssignment", assignment_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        old_values=old_vals or None,
        new_values=new_vals or None,
    )
    return result


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń przydział godzin")
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> None:
    old_orm = get_teaching_load_by_id(db, assignment_id)
    old = _build_dto(old_orm) if old_orm else None
    if not delete_teaching_load(db, assignment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału")
    _user_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "TeachingLoadAssignment", assignment_id, "delete",
        modified_by=current_user.user_id,
        modified_by_name=_user_label,
        old_values={
            "teacher": f"{old.teacher_title or ''} {old.teacher_first_name} {old.teacher_last_name}".strip() if old else None,
            "subject_name": old.subject_name if old else None,
            "activity_name": old.activity_name if old else None,
            "semester_name": old.semester_name if old else None,
            "hours": old.hours if old else None,
            "field_of_study_label": old.field_of_study_label if old else None,
            "group_label": old.group_label if old else None,
        } if old else None,
    )
