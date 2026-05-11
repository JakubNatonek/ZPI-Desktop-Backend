from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_audit import log_change
from app.cruds.crud_teaching_load import (
    create_teaching_load,
    delete_teaching_load,
    get_teaching_load_by_id,
    get_teaching_loads,
    map_teaching_load_to_response,
    patch_teaching_load,
    update_teaching_load,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.teaching_load import (
    TeachingLoadAssignmentCreate,
    TeachingLoadAssignmentListResponse,
    TeachingLoadAssignmentPatch,
    TeachingLoadAssignmentResponse,
    TeachingLoadAssignmentUpdate,
)


router = APIRouter(prefix="/teaching-loads", tags=["teaching-loads"])


@router.get("/list", response_model=TeachingLoadAssignmentListResponse, summary="Lista przydzialow godzin")
def list_teaching_loads(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "rapla_editor"])),
) -> TeachingLoadAssignmentListResponse:
    assignments = get_teaching_loads(db)
    return TeachingLoadAssignmentListResponse(
        items=[TeachingLoadAssignmentResponse(**map_teaching_load_to_response(item)) for item in assignments]
    )


@router.get("/{assignment_id}", response_model=TeachingLoadAssignmentResponse, summary="Szczegoly przydzialu godzin")
def get_teaching_load_entry(
    assignment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "rapla_editor"])),
) -> TeachingLoadAssignmentResponse:
    assignment = get_teaching_load_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału godzin")

    return TeachingLoadAssignmentResponse(**map_teaching_load_to_response(assignment))


@router.post("", response_model=TeachingLoadAssignmentResponse, status_code=status.HTTP_201_CREATED, summary="Dodaj przydzial godzin")
def create_teaching_load_entry(
    payload: TeachingLoadAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor"])),
) -> TeachingLoadAssignmentResponse:
    assignment = create_teaching_load(db, payload)
    response_payload = TeachingLoadAssignmentResponse(**map_teaching_load_to_response(assignment))

    log_change(
        db=db,
        entity_name="TeachingLoadAssignment",
        entity_id=assignment.id,
        action="CREATE",
        old_values=None,
        new_values=response_payload.model_dump(mode="json"),
        user_id=current_user.user_id,
    )

    return response_payload


@router.put("/{assignment_id}", response_model=TeachingLoadAssignmentResponse, summary="Zaktualizuj przydzial godzin")
def update_teaching_load_entry(
    assignment_id: int,
    payload: TeachingLoadAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor"])),
) -> TeachingLoadAssignmentResponse:
    assignment = get_teaching_load_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału godzin")

    old_values = map_teaching_load_to_response(assignment)

    updated = update_teaching_load(db, assignment, payload)
    response_payload = TeachingLoadAssignmentResponse(**map_teaching_load_to_response(updated))

    log_change(
        db=db,
        entity_name="TeachingLoadAssignment",
        entity_id=updated.id,
        action="UPDATE",
        old_values=old_values,
        new_values=response_payload.model_dump(mode="json"),
        user_id=current_user.user_id,
    )

    return response_payload


@router.patch("/{assignment_id}", response_model=TeachingLoadAssignmentResponse, summary="Edytuj przydzial godzin (inline)")
def patch_teaching_load_entry(
    assignment_id: int,
    payload: TeachingLoadAssignmentPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor"])),
) -> TeachingLoadAssignmentResponse:
    assignment = get_teaching_load_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału godzin")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nie podano żadnych zmian")

    old_values = map_teaching_load_to_response(assignment)

    updated = patch_teaching_load(db, assignment, payload)
    response_payload = TeachingLoadAssignmentResponse(**map_teaching_load_to_response(updated))

    log_change(
        db=db,
        entity_name="TeachingLoadAssignment",
        entity_id=updated.id,
        action="UPDATE",
        old_values=old_values,
        new_values=response_payload.model_dump(mode="json"),
        user_id=current_user.user_id,
    )

    return response_payload


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usun przydzial godzin")
def delete_teaching_load_entry(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor"])),
) -> None:
    assignment = get_teaching_load_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono przydziału godzin")

    old_values = map_teaching_load_to_response(assignment)
    delete_teaching_load(db, assignment)

    log_change(
        db=db,
        entity_name="TeachingLoadAssignment",
        entity_id=assignment_id,
        action="DELETE",
        old_values=old_values,
        new_values=None,
        user_id=current_user.user_id,
    )
