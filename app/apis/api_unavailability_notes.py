from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
from app.cruds.crud_unavailability_notes import (
    create_unavailability_note,
    get_unavailability_notes_for_user,
    get_all_unavailability_notes,
    get_pending_unavailability_notes,
    update_unavailability_note_status,
    get_unavailability_note_by_id,
)
from app.models.model_user import User
from app.schemas.unavailability_note import (
    UnavailabilityNoteCreate,
    UnavailabilityNoteUpdate,
    UnavailabilityNoteResponse,
    UnavailabilityNoteListResponse,
)


router = APIRouter(prefix="/unavailability-notes", tags=["unavailability-notes"])


@router.post(
    "",
    response_model=UnavailabilityNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nową notatkę o niedostępności",
)
async def create_note(
    payload: UnavailabilityNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnavailabilityNoteResponse:
    """
    Tworzy nową notatkę o niedostępności dla zalogowanego użytkownika.
    Automatycznie powiadamia adminów.
    Dostęp: zalogowany użytkownik (Wykładowca)
    """
    if payload.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można zgłosić niedostępności z datą wsteczną",
        )

    if payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date nie może być wcześniejsza niż start_date",
        )

    try:
        note, created_notifications = create_unavailability_note(
            db=db,
            user_id=current_user.user_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            description=payload.description,
            note_type=payload.note_type,
        )
        create_audit_log(
            db, "UnavailabilityNote", int(note.id), "create",
            modified_by=current_user.user_id,
            modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
            new_values={
                "user_id": note.user_id,
                "start_date": str(note.start_date),
                "end_date": str(note.end_date) if note.end_date else None,
                "description": note.description,
                "note_type": note.note_type.value if note.note_type else None,
                "status": note.status.value if note.status else None,
            },
        )
        return UnavailabilityNoteResponse.model_validate(note)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=list[UnavailabilityNoteResponse],
    summary="Pobierz swoje notatki",
)
def get_my_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UnavailabilityNoteResponse]:
    """
    Zwraca wszystkie notatki o niedostępności dla zalogowanego użytkownika.
    Dostęp: zalogowany użytkownik
    """
    notes = get_unavailability_notes_for_user(db, current_user.user_id)
    return [UnavailabilityNoteResponse.model_validate(note) for note in notes]


@router.get(
    "/all",
    response_model=list[UnavailabilityNoteListResponse],
    summary="Pobierz wszystkie notatki (Admin)",
)
def get_all_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UnavailabilityNoteListResponse]:
    """
    Zwraca wszystkie notatki o niedostępności dla wszystkich użytkowników.
    Dostęp: Admin
    """
    if not user_has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu. Wymagana rola: Admin",
        )

    notes_with_users = get_all_unavailability_notes(db)
    result = []
    for note, user in notes_with_users:
        note_dict = UnavailabilityNoteResponse.model_validate(note).model_dump()
        note_dict["first_name"] = user.first_name
        note_dict["last_name"] = user.last_name
        result.append(UnavailabilityNoteListResponse(**note_dict))

    return result


@router.get(
    "/all/pending",
    response_model=list[UnavailabilityNoteListResponse],
    summary="Pobierz notatki oczekujące (Admin)",
)
def get_pending_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UnavailabilityNoteListResponse]:
    """
    Zwraca notatki o statusie 'pending' (oczekujące na rozpatrzenie).
    Dostęp: Admin
    """
    if not user_has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu. Wymagana rola: Admin",
        )

    notes_with_users = get_pending_unavailability_notes(db)
    result = []
    for note, user in notes_with_users:
        note_dict = UnavailabilityNoteResponse.model_validate(note).model_dump()
        note_dict["first_name"] = user.first_name
        note_dict["last_name"] = user.last_name
        result.append(UnavailabilityNoteListResponse(**note_dict))

    return result


@router.put(
    "/{note_id}/status",
    response_model=UnavailabilityNoteResponse,
    summary="Zmień status notatki (Admin)",
)
def update_note_status(
    note_id: int,
    payload: UnavailabilityNoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnavailabilityNoteResponse:
    """
    Zmienia status notatki na 'accepted', 'rejected' lub 'acknowledged'.
    Automatycznie powiadamia autora notatki o zmianie statusu.
    Dostęp: Admin
    """
    if not user_has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu. Wymagana rola: Admin",
        )

    note = update_unavailability_note_status(db, note_id, payload.status)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notatka o ID {note_id} nie znaleziona",
        )

    create_audit_log(
        db, "UnavailabilityNote", note_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        new_values={"status": note.status.value if note.status else None},
    )
    return UnavailabilityNoteResponse.model_validate(note)


@router.get(
    "/{note_id}",
    response_model=UnavailabilityNoteResponse,
    summary="Pobierz szczegóły notatki",
)
def get_note_detail(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UnavailabilityNoteResponse:
    """
    Zwraca szczegóły konkretnej notatki.
    Użytkownik może zobaczyć tylko swoją notatkę, chyba że jest Adminem.
    Dostęp: zalogowany użytkownik
    """
    note = get_unavailability_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notatka o ID {note_id} nie znaleziona",
        )

    # Sprawdź uprawnienia
    is_admin = user_has_role(current_user, "admin")
    is_owner = note.user_id == current_user.user_id

    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu do tej notatki",
        )

    return UnavailabilityNoteResponse.model_validate(note)
