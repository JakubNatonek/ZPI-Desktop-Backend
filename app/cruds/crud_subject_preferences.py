from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.model_subject_preference import SubjectPreference
from app.models.model_subject import Subject


def get_preferences_for_user(db: Session, user_id: int) -> list[SubjectPreference]:
    """
    Retrieve all subject preferences for a specific user.
    Uses selectinload to avoid N+1 queries.
    """
    return (
        db.query(SubjectPreference)
        .options(selectinload(SubjectPreference.subject))
        .filter(SubjectPreference.user_id == user_id)
        .all()
    )


def add_preference(db: Session, user_id: int, subject_id: int) -> SubjectPreference:
    """
    Add a subject preference for a user.
    Verifies that the preference doesn't already exist.
    """
    # Check if preference already exists
    existing_preference = (
        db.query(SubjectPreference)
        .filter(
            SubjectPreference.user_id == user_id,
            SubjectPreference.subject_id == subject_id,
        )
        .first()
    )

    if existing_preference is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} already has preference for subject {subject_id}",
        )

    # Verify subject exists
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} not found",
        )

    # Create new preference
    preference = SubjectPreference(user_id=user_id, subject_id=subject_id)
    db.add(preference)
    db.commit()

    return preference


def remove_preference(db: Session, user_id: int, subject_id: int) -> None:
    """
    Remove a subject preference for a user.
    Raises 404 if preference doesn't exist.
    """
    preference = (
        db.query(SubjectPreference)
        .filter(
            SubjectPreference.user_id == user_id,
            SubjectPreference.subject_id == subject_id,
        )
        .first()
    )

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No preference found for user {user_id} and subject {subject_id}",
        )

    db.delete(preference)
    db.commit()
