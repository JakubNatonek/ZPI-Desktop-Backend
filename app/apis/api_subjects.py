from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
from app.cruds.crud_subject import (
    create_subject,
    delete_subject,
    get_subject_by_id,
    get_subject_by_name_and_activity,
    get_subjects,
    map_subject_to_response,
    update_subject,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.subject import SubjectCreate, SubjectListResponse, SubjectResponse, SubjectUpdate


router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/public/list", response_model=SubjectListResponse, summary="Pobierz publiczną listę przedmiotów")
def list_subjects_public(
    db: Session = Depends(get_db),
) -> SubjectListResponse:
    subjects = get_subjects(db)
    return SubjectListResponse(items=[SubjectResponse(**map_subject_to_response(subject)) for subject in subjects])


@router.get("/list", response_model=SubjectListResponse, summary="Pobierz listę przedmiotów")
def list_subjects(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectListResponse:
    subjects = get_subjects(db)
    return SubjectListResponse(items=[SubjectResponse(**map_subject_to_response(subject)) for subject in subjects])


@router.get("/{subject_id}", response_model=SubjectResponse, summary="Pobierz szczegóły przedmiotu")
def get_subject_entry(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectResponse:
    subject = get_subject_by_id(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    return SubjectResponse(**map_subject_to_response(subject))


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz przedmiot")
def create_subject_entry(
    payload: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> SubjectResponse:
    if not payload.name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject name cannot be empty")

    existing = get_subject_by_name_and_activity(db, payload.name, payload.activity_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subject with selected activity already exists",
        )

    try:
        created = create_subject(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    create_audit_log(
        db, "Subject", int(created.id), "create",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        new_values=map_subject_to_response(created),
    )
    return SubjectResponse(**map_subject_to_response(created))


@router.put("/{subject_id}", response_model=SubjectResponse, summary="Zaktualizuj przedmiot")
def update_subject_entry(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> SubjectResponse:
    subject = get_subject_by_id(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    existing = get_subject_by_name_and_activity(db, payload.name, payload.activity_id)
    if existing is not None and existing.id != subject_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subject with selected activity already exists",
        )

    old_values = map_subject_to_response(subject)
    try:
        updated = update_subject(db, subject, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    create_audit_log(
        db, "Subject", subject_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        old_values=old_values,
        new_values=map_subject_to_response(updated),
    )
    return SubjectResponse(**map_subject_to_response(updated))


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń przedmiot")
def delete_subject_entry(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> None:
    subject = get_subject_by_id(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    old_values = map_subject_to_response(subject)
    delete_subject(db, subject)
    create_audit_log(
        db, "Subject", subject_id, "delete",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        old_values=old_values,
    )
