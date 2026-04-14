from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session, selectinload

from app.cruds.crud_activity import get_activity_by_id
from app.models.model_subject import Subject
from app.models.model_subject_activity import SubjectActivity
from app.schemas.subject import SubjectCreate, SubjectUpdate


def _normalize_required_text(value: str) -> str:
    return value.strip()


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


def _resolve_activity_id(db: Session, activity_id: int) -> int:
    activity = get_activity_by_id(db, activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown activity id: {activity_id}",
        )

    return int(activity.id)


def _load_subject_with_relations(db: Session, subject_id: int) -> Optional[Subject]:
    return (
        db.query(Subject)
        .options(
            selectinload(Subject.type_link).selectinload(SubjectActivity.activity),
            selectinload(Subject.subject_activities).selectinload(SubjectActivity.activity),
        )
        .filter(Subject.id == subject_id)
        .first()
    )


def _sync_subject_id_sequence(db: Session) -> None:
    db.execute(
        text(
            "SELECT setval(pg_get_serial_sequence('subject', 'id'), COALESCE((SELECT MAX(id) FROM subject), 0) + 1, false)"
        )
    )


def get_subjects(db: Session) -> list[Subject]:
    return (
        db.query(Subject)
        .options(
            selectinload(Subject.type_link).selectinload(SubjectActivity.activity),
            selectinload(Subject.subject_activities).selectinload(SubjectActivity.activity),
        )
        .order_by(Subject.name.asc(), Subject.id.asc())
        .all()
    )


def get_subject_by_id(db: Session, subject_id: int) -> Optional[Subject]:
    return _load_subject_with_relations(db, subject_id)


def get_subject_by_name_and_activity(db: Session, name: str, activity_id: int) -> Optional[Subject]:
    cleaned_name = _normalize_required_text(name)
    if not cleaned_name:
        return None

    return (
        db.query(Subject)
        .join(SubjectActivity, Subject.type_id == SubjectActivity.id)
        .filter(
            Subject.name == cleaned_name,
            SubjectActivity.activity_id == activity_id,
        )
        .first()
    )


def _ensure_primary_subject_activity_link(db: Session, subject: Subject, activity_id: int) -> None:
    if subject.type_id is not None:
        current_link = (
            db.query(SubjectActivity)
            .filter(
                SubjectActivity.id == subject.type_id,
                SubjectActivity.subject_id == subject.id,
            )
            .first()
        )
        if current_link is not None:
            existing_target_link = (
                db.query(SubjectActivity)
                .filter(
                    SubjectActivity.subject_id == subject.id,
                    SubjectActivity.activity_id == activity_id,
                )
                .first()
            )
            if existing_target_link is not None and existing_target_link.id != current_link.id:
                subject.type_id = int(existing_target_link.id)
                db.delete(current_link)
                db.flush()
                return

            current_link.activity_id = activity_id
            db.add(current_link)
            db.flush()
            return

    existing_link = (
        db.query(SubjectActivity)
        .filter(
            SubjectActivity.subject_id == subject.id,
            SubjectActivity.activity_id == activity_id,
        )
        .first()
    )
    if existing_link is not None:
        subject.type_id = int(existing_link.id)
        return

    link = SubjectActivity(subject_id=subject.id, activity_id=activity_id)
    db.add(link)
    db.flush()
    subject.type_id = int(link.id)


def _prune_non_primary_links(db: Session, subject: Subject) -> None:
    if subject.type_id is None:
        return

    (
        db.query(SubjectActivity)
        .filter(
            SubjectActivity.subject_id == subject.id,
            SubjectActivity.id != subject.type_id,
        )
        .delete(synchronize_session=False)
    )


def create_subject(db: Session, payload: SubjectCreate) -> Subject:
    cleaned_name = _normalize_required_text(payload.name)
    if not cleaned_name:
        raise ValueError("Subject name cannot be empty")

    activity_id = _resolve_activity_id(db, payload.activity_id)
    _sync_subject_id_sequence(db)

    subject = Subject(
        name=cleaned_name,
        type_id=None,
        type_display=_normalize_optional_text(payload.type_display),
        room_properties=_normalize_optional_text(payload.room_properties),
        blocked=bool(payload.blocked),
        periodic=bool(payload.periodic),
    )
    db.add(subject)
    db.flush()

    _ensure_primary_subject_activity_link(db, subject, activity_id)
    _prune_non_primary_links(db, subject)

    db.add(subject)
    db.commit()

    loaded = _load_subject_with_relations(db, int(subject.id))
    return loaded if loaded is not None else subject


def update_subject(db: Session, subject: Subject, payload: SubjectUpdate) -> Subject:
    cleaned_name = _normalize_required_text(payload.name)
    if not cleaned_name:
        raise ValueError("Subject name cannot be empty")

    activity_id = _resolve_activity_id(db, payload.activity_id)

    subject.name = cleaned_name
    subject.type_display = _normalize_optional_text(payload.type_display)
    subject.room_properties = _normalize_optional_text(payload.room_properties)
    subject.blocked = bool(payload.blocked)
    subject.periodic = bool(payload.periodic)

    _ensure_primary_subject_activity_link(db, subject, activity_id)
    _prune_non_primary_links(db, subject)

    db.add(subject)
    db.commit()

    loaded = _load_subject_with_relations(db, int(subject.id))
    return loaded if loaded is not None else subject


def delete_subject(db: Session, subject: Subject) -> None:
    db.delete(subject)
    db.commit()


def map_subject_to_response(subject: Subject) -> dict:
    primary_link = subject.type_link
    primary_activity = primary_link.activity if primary_link is not None else None

    return {
        "id": subject.id,
        "name": subject.name,
        "type_id": subject.type_id,
        "activity_id": primary_activity.id if primary_activity is not None else None,
        "activity_name": primary_activity.name if primary_activity is not None else None,
        "type_display": subject.type_display,
        "room_properties": subject.room_properties,
        "blocked": subject.blocked,
        "periodic": subject.periodic,
    }
