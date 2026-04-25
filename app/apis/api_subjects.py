from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
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

SUBJECT_NOT_FOUND_DETAIL = "Subject not found"
SUBJECT_CONFLICT_DETAIL = "Subject with selected activity already exists"


def _to_subject_response(subject) -> SubjectResponse:
    return SubjectResponse(**map_subject_to_response(subject))


def _get_subject_or_404(db: Session, subject_id: int):
    subject = get_subject_by_id(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SUBJECT_NOT_FOUND_DETAIL)
    return subject


@router.get("/list", response_model=SubjectListResponse, summary="Pobierz listę przedmiotów")
def list_subjects(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectListResponse:
    subjects = get_subjects(db)
    return SubjectListResponse(items=[_to_subject_response(subject) for subject in subjects])


@router.get("/{subject_id}", response_model=SubjectResponse, summary="Pobierz szczegóły przedmiotu")
def get_subject_entry(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectResponse:
    subject = _get_subject_or_404(db, subject_id)
    return _to_subject_response(subject)


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz przedmiot")
def create_subject_entry(
    payload: SubjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectResponse:
    cleaned_name = payload.name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject name cannot be empty")

    existing = get_subject_by_name_and_activity(db, cleaned_name, payload.activity_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=SUBJECT_CONFLICT_DETAIL,
        )

    try:
        created = create_subject(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _to_subject_response(created)


@router.put("/{subject_id}", response_model=SubjectResponse, summary="Zaktualizuj przedmiot")
def update_subject_entry(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SubjectResponse:
    subject = _get_subject_or_404(db, subject_id)

    cleaned_name = payload.name.strip()

    existing = get_subject_by_name_and_activity(db, cleaned_name, payload.activity_id)
    if existing is not None and existing.id != subject_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=SUBJECT_CONFLICT_DETAIL,
        )

    try:
        updated = update_subject(db, subject, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _to_subject_response(updated)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń przedmiot")
def delete_subject_entry(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    subject = _get_subject_or_404(db, subject_id)
    delete_subject(db, subject)
