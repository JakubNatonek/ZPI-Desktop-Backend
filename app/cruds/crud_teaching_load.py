from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.model_activity import Activity
from app.models.model_field_of_study import FieldOfStudy
from app.models.model_semestr import Semestr
from app.models.model_subject import Subject
from app.models.model_subject_activity import SubjectActivity
from app.models.model_subject_for_field_of_study import SubjectForFieldOfStudy
from app.models.model_teaching_load_assignment import TeachingLoadAssignment
from app.models.model_user import User
from app.cruds.crud_field_of_study import get_field_of_study_by_id
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_subject_for_field_of_study import add_subject_to_field_of_study
from app.schemas.teaching_load import (
    TeachingLoadAssignmentCreate,
    TeachingLoadAssignmentPatch,
    TeachingLoadAssignmentUpdate,
)


def _load_with_relations(db: Session, assignment_id: int) -> Optional[TeachingLoadAssignment]:
    return (
        db.query(TeachingLoadAssignment)
        .options(
            selectinload(TeachingLoadAssignment.teacher).selectinload(User.teacher_profile),
            selectinload(TeachingLoadAssignment.subject),
            selectinload(TeachingLoadAssignment.activity),
            selectinload(TeachingLoadAssignment.semester),
            selectinload(TeachingLoadAssignment.subject_for_field_of_study).selectinload(
                SubjectForFieldOfStudy.field_of_study
            ),
        )
        .filter(TeachingLoadAssignment.id == assignment_id)
        .first()
    )


def _is_lecturer_user(db: Session, teacher_id: int) -> bool:
    role_names = {
        str(role.name).strip().lower()
        for role in get_roles_for_user(db, teacher_id)
        if role.name
    }
    return "wykladowca" in role_names or "lecturer" in role_names


def _get_teacher(db: Session, teacher_id: int) -> User:
    teacher = db.query(User).filter(User.user_id == teacher_id).first()
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown teacher id: {teacher_id}",
        )
    if not _is_lecturer_user(db, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {teacher_id} is not a teacher",
        )
    return teacher


def _get_subject(db: Session, subject_id: int) -> Subject:
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown subject id: {subject_id}",
        )
    return subject


def _get_activity(db: Session, activity_id: int) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown activity id: {activity_id}",
        )
    return activity


def _get_semester(db: Session, semester_id: int) -> Semestr:
    semester = db.query(Semestr).filter(Semestr.id == semester_id).first()
    if semester is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown semester id: {semester_id}",
        )
    return semester


def _get_field_of_study(db: Session, field_of_study_id: int) -> FieldOfStudy:
    field_of_study = get_field_of_study_by_id(db, field_of_study_id)
    if field_of_study is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown field of study id: {field_of_study_id}",
        )
    return field_of_study


def _ensure_subject_activity_link(db: Session, subject_id: int, activity_id: int) -> None:
    link = (
        db.query(SubjectActivity)
        .filter(
            SubjectActivity.subject_id == subject_id,
            SubjectActivity.activity_id == activity_id,
        )
        .first()
    )
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wybrany typ zajęć nie jest powiązany z tym przedmiotem",
        )


def _get_existing_assignment(
    db: Session,
    teacher_id: int,
    subject_id: int,
    activity_id: int,
    semester_id: int,
    subject_for_field_of_study_id: int | None,
) -> Optional[TeachingLoadAssignment]:
    return (
        db.query(TeachingLoadAssignment)
        .filter(
            TeachingLoadAssignment.teacher_id == teacher_id,
            TeachingLoadAssignment.subject_id == subject_id,
            TeachingLoadAssignment.activity_id == activity_id,
            TeachingLoadAssignment.semester_id == semester_id,
            TeachingLoadAssignment.subject_for_field_of_study_id == subject_for_field_of_study_id,
        )
        .first()
    )


def get_teaching_loads(db: Session) -> list[TeachingLoadAssignment]:
    return (
        db.query(TeachingLoadAssignment)
        .options(
            selectinload(TeachingLoadAssignment.teacher).selectinload(User.teacher_profile),
            selectinload(TeachingLoadAssignment.subject),
            selectinload(TeachingLoadAssignment.activity),
            selectinload(TeachingLoadAssignment.semester),
            selectinload(TeachingLoadAssignment.subject_for_field_of_study).selectinload(
                SubjectForFieldOfStudy.field_of_study
            ),
        )
        .order_by(
            TeachingLoadAssignment.semester_id.asc(),
            TeachingLoadAssignment.teacher_id.asc(),
            TeachingLoadAssignment.subject_id.asc(),
            TeachingLoadAssignment.activity_id.asc(),
            TeachingLoadAssignment.id.asc(),
        )
        .all()
    )


def get_teaching_load_by_id(db: Session, assignment_id: int) -> Optional[TeachingLoadAssignment]:
    return _load_with_relations(db, assignment_id)


def create_teaching_load(
    db: Session,
    payload: TeachingLoadAssignmentCreate,
) -> TeachingLoadAssignment:
    _get_teacher(db, payload.teacher_id)
    _get_subject(db, payload.subject_id)
    _get_activity(db, payload.activity_id)
    _get_semester(db, payload.semester_id)
    if payload.field_of_study_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wybierz poprawny rocznik",
        )
    _get_field_of_study(db, payload.field_of_study_id)
    _ensure_subject_activity_link(db, payload.subject_id, payload.activity_id)

    subject_field_mapping = add_subject_to_field_of_study(
        db,
        subject_id=payload.subject_id,
        field_of_study_id=payload.field_of_study_id,
    )

    existing = _get_existing_assignment(
        db,
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        activity_id=payload.activity_id,
        semester_id=payload.semester_id,
        subject_for_field_of_study_id=subject_field_mapping.id,
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Przydział godzin już istnieje",
        )

    assignment = TeachingLoadAssignment(
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        activity_id=payload.activity_id,
        semester_id=payload.semester_id,
        hours=payload.hours,
        subject_for_field_of_study_id=subject_field_mapping.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return _load_with_relations(db, int(assignment.id)) or assignment


def update_teaching_load(
    db: Session,
    assignment: TeachingLoadAssignment,
    payload: TeachingLoadAssignmentUpdate,
) -> TeachingLoadAssignment:
    _get_teacher(db, payload.teacher_id)
    _get_subject(db, payload.subject_id)
    _get_activity(db, payload.activity_id)
    _get_semester(db, payload.semester_id)
    if payload.field_of_study_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wybierz poprawny rocznik",
        )
    _get_field_of_study(db, payload.field_of_study_id)
    _ensure_subject_activity_link(db, payload.subject_id, payload.activity_id)

    subject_field_mapping = add_subject_to_field_of_study(
        db,
        subject_id=payload.subject_id,
        field_of_study_id=payload.field_of_study_id,
    )

    existing = _get_existing_assignment(
        db,
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        activity_id=payload.activity_id,
        semester_id=payload.semester_id,
        subject_for_field_of_study_id=subject_field_mapping.id,
    )
    if existing is not None and existing.id != assignment.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Przydział godzin już istnieje",
        )

    assignment.teacher_id = payload.teacher_id
    assignment.subject_id = payload.subject_id
    assignment.activity_id = payload.activity_id
    assignment.semester_id = payload.semester_id
    assignment.hours = payload.hours
    assignment.subject_for_field_of_study_id = subject_field_mapping.id

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return _load_with_relations(db, int(assignment.id)) or assignment


def patch_teaching_load(
    db: Session,
    assignment: TeachingLoadAssignment,
    payload: TeachingLoadAssignmentPatch,
) -> TeachingLoadAssignment:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return assignment

    if "teacher_id" in data:
        _get_teacher(db, data["teacher_id"])
    if "subject_id" in data:
        _get_subject(db, data["subject_id"])
    if "activity_id" in data:
        _get_activity(db, data["activity_id"])
    if "semester_id" in data:
        _get_semester(db, data["semester_id"])
    if "field_of_study_id" in data and data["field_of_study_id"] is not None:
        _get_field_of_study(db, data["field_of_study_id"])

    target_teacher_id = data.get("teacher_id", assignment.teacher_id)
    target_subject_id = data.get("subject_id", assignment.subject_id)
    target_activity_id = data.get("activity_id", assignment.activity_id)
    target_semester_id = data.get("semester_id", assignment.semester_id)
    target_field_of_study_id = data.get("field_of_study_id")

    if target_field_of_study_id is None and assignment.subject_for_field_of_study is not None:
        target_field_of_study_id = assignment.subject_for_field_of_study.field_of_study_id

    _ensure_subject_activity_link(db, target_subject_id, target_activity_id)

    subject_field_mapping = None
    if target_field_of_study_id is not None:
        subject_field_mapping = add_subject_to_field_of_study(
            db,
            subject_id=target_subject_id,
            field_of_study_id=target_field_of_study_id,
        )
    elif assignment.subject_for_field_of_study is not None:
        subject_field_mapping = assignment.subject_for_field_of_study

    existing = _get_existing_assignment(
        db,
        teacher_id=target_teacher_id,
        subject_id=target_subject_id,
        activity_id=target_activity_id,
        semester_id=target_semester_id,
        subject_for_field_of_study_id=subject_field_mapping.id if subject_field_mapping is not None else None,
    )
    if existing is not None and existing.id != assignment.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Przydział godzin już istnieje",
        )

    for field_name, value in data.items():
        setattr(assignment, field_name, value)

    if subject_field_mapping is not None:
        assignment.subject_for_field_of_study_id = subject_field_mapping.id

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return _load_with_relations(db, int(assignment.id)) or assignment


def delete_teaching_load(db: Session, assignment: TeachingLoadAssignment) -> None:
    db.delete(assignment)
    db.commit()


def map_teaching_load_to_response(assignment: TeachingLoadAssignment) -> dict:
    teacher = assignment.teacher
    teacher_profile = teacher.teacher_profile if teacher is not None else None
    subject = assignment.subject
    activity = assignment.activity
    semester = assignment.semester
    subject_field = assignment.subject_for_field_of_study
    field_of_study = subject_field.field_of_study if subject_field is not None else None
    field_of_study_label = None
    if field_of_study is not None:
        field_of_study_label = f"{field_of_study.name} / {field_of_study.abbrevation} / {field_of_study.year}"

    return {
        "id": assignment.id,
        "teacher_id": assignment.teacher_id,
        "teacher_title": teacher_profile.title if teacher_profile else None,
        "teacher_first_name": teacher.first_name if teacher else None,
        "teacher_last_name": teacher.last_name if teacher else None,
        "subject_id": assignment.subject_id,
        "subject_name": subject.name if subject else None,
        "activity_id": assignment.activity_id,
        "activity_name": activity.name if activity else None,
        "semester_id": assignment.semester_id,
        "semester_name": semester.nazwa if semester else None,
        "field_of_study_id": subject_field.field_of_study_id if subject_field is not None else None,
        "field_of_study_label": field_of_study_label,
        "hours": assignment.hours,
    }
