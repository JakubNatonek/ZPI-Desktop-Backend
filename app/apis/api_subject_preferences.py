from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_subject_preferences import (
    add_preference,
    get_preferences_for_user,
    remove_preference,
)
from app.models.model_user import User
from app.schemas.subject_preference import SubjectPreferenceCreate, SubjectPreferenceResponse


router = APIRouter(prefix="/subject-preferences", tags=["subject-preferences"])


def _verify_authorization(current_user: User, target_user_id: int) -> None:
    """Verify that current user has permission to access target user's preferences."""
    is_admin = user_has_role(current_user, "admin")
    if not is_admin and current_user.user_id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own preferences",
        )


@router.get("/{user_id}", response_model=list[SubjectPreferenceResponse], summary="Pobierz preferencje przedmiotów użytkownika")
def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SubjectPreferenceResponse]:
    _verify_authorization(current_user, user_id)
    
    preferences = get_preferences_for_user(db, user_id)
    return [
        SubjectPreferenceResponse(
            id=pref.id,
            user_id=pref.user_id,
            subject_id=pref.subject_id,
            subject_name=pref.subject.name if pref.subject else None,
        )
        for pref in preferences
    ]


@router.post("/{user_id}/add", response_model=SubjectPreferenceResponse, status_code=status.HTTP_201_CREATED, summary="Dodaj preferencję przedmiotu")
def add_user_preference(
    user_id: int,
    payload: SubjectPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubjectPreferenceResponse:
    _verify_authorization(current_user, user_id)
    
    # Use provided user_id from path, not from payload
    preference = add_preference(db, user_id, payload.subject_id)
    
    return SubjectPreferenceResponse(
        id=preference.id,
        user_id=preference.user_id,
        subject_id=preference.subject_id,
        subject_name=preference.subject.name if preference.subject else None,
    )


@router.delete("/{user_id}/remove/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń preferencję przedmiotu")
def remove_user_preference(
    user_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _verify_authorization(current_user, user_id)
    
    remove_preference(db, user_id, subject_id)
