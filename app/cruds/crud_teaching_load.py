from datetime import date, datetime, timedelta, timezone
from typing import Optional, cast
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.cruds.crud_department_for_field_of_study import get_departments_for_field_of_study
from app.cruds.crud_field_of_study_for_group import get_groups_from_maping_by_field_of_study_id
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
from app.cruds.crud_subject_for_field_of_study import (
    add_subject_to_field_of_study,
    get_primary_field_of_study_for_subject,
)
from app.cruds.rapla.crud_rapla_app_user_to_resourc import get_resorsc_by_user_id
from app.cruds.rapla.crud_rapla_group_to_resourc import get_resourc_by_group_id
from app.cruds.rapla.crud_rapla_room_to_resourc import get_resorsc_by_room_id
from app.cruds.rapla.crud_rapla_subject_to_resourc import get_resourc_by_subject_id
from app.cruds.rapla.crud_rapla_users import get_first_rapla_users_by_username
from app.cruds.rapla.rapla_format_datetime import format_rapla_date
from app.cruds.room.crud_room import get_room_by_id
from app.schemas.teaching_load import (
    TeachingLoadAssignmentCreate,
    TeachingLoadAssignmentPatch,
    TeachingLoadAssignmentUpdate,
)
from app.schemas.rapla.reservations.schema_rapla_apontment import SchemaRaplaApointment
from app.schemas.rapla.reservations.schema_rapla_reservation_zajencia import SchemaRaplaReservationZajencia
from app.schemas.rapla.schema_rapla_permision import RaplaPermission


def _load_with_relations(db: Session, assignment_id: int) -> Optional[TeachingLoadAssignment]:
    return (
        db.query(TeachingLoadAssignment)
        .options(
            selectinload(TeachingLoadAssignment.teacher).selectinload(User.teacher_profile),
            selectinload(TeachingLoadAssignment.subject),
            selectinload(TeachingLoadAssignment.activity),
            selectinload(TeachingLoadAssignment.semester),
            selectinload(TeachingLoadAssignment.room),
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


def _get_room(db: Session, room_id: int) -> None:
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown room id: {room_id}",
        )


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
            selectinload(TeachingLoadAssignment.room),
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
    if payload.room_id is not None:
        _get_room(db, payload.room_id)
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
        room_id=payload.room_id,
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
    if payload.room_id is not None:
        _get_room(db, payload.room_id)
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
    assignment.room_id = payload.room_id

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
    if "room_id" in data and data["room_id"] is not None:
        _get_room(db, data["room_id"])
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
    room = assignment.room
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
        "room_id": assignment.room_id,
        "room_number": room.number if room is not None else None,
        "hours": assignment.hours,
    }


def teaching_load_assignments_to_schema(db: Session) -> list[SchemaRaplaReservationZajencia]:
    assignments = (
        db.query(TeachingLoadAssignment)
        .options(
            selectinload(TeachingLoadAssignment.teacher),
            selectinload(TeachingLoadAssignment.subject),
            selectinload(TeachingLoadAssignment.semester),
            selectinload(TeachingLoadAssignment.room),
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

    owner = get_first_rapla_users_by_username(db, "system")
    owner_uuid = cast(str, owner.uuid) if owner is not None else ""

    now = datetime.now(timezone.utc)
    created_at = now.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    last_changed = created_at

    reservations_by_key: dict[str, SchemaRaplaReservationZajencia] = {}
    for assignment in assignments:
        semester = assignment.semester
        if semester is None or semester.data_rozpoczecia is None or semester.data_zakonczenia is None:
            # TODO: missing semester dates for this teaching load assignment.
            continue

        # lesson_date = cast(date, assignment.date)  # TODO: teaching load assignment has no single lesson date.
        # start_time = cast(time, assignment.start_time).strftime("%H:%M:%S")  # TODO: missing start time.
        start_time = "07:00:00"
        # end_time = cast(time, assignment.end_time).strftime("%H:%M:%S")  # TODO: missing end time.

        allocate: list[str] = []
        field_of_study_id = None
        if assignment.subject_for_field_of_study is not None:
            field_of_study_id = assignment.subject_for_field_of_study.field_of_study_id
        elif getattr(assignment, "subject_id", None) is not None:
            field_of_study = get_primary_field_of_study_for_subject(db, cast(int, assignment.subject_id))
            if field_of_study is not None:
                field_of_study_id = cast(int, getattr(field_of_study, "id", None))

        if field_of_study_id is not None:
            groups = get_groups_from_maping_by_field_of_study_id(db, field_of_study_id)
            for group in groups:
                group_resource = get_resourc_by_group_id(db, cast(int, group.id))
                if group_resource is not None and getattr(group_resource, "uuid", None):
                    allocate.append(cast(str, group_resource.uuid))
        # TODO: add group mapping for teaching loads when field_of_study_id is missing.

        subject_resource = get_resourc_by_subject_id(db, cast(int, assignment.subject_id))
        if subject_resource is not None and getattr(subject_resource, "uuid", None):
            allocate.append(cast(str, subject_resource.uuid))

        if getattr(assignment, "room_id", None) is not None:
            room_resource = get_resorsc_by_room_id(db, cast(int, assignment.room_id))
            if room_resource is not None and getattr(room_resource, "uuid", None):
                allocate.append(cast(str, room_resource.uuid))

        teacher_resource = get_resorsc_by_user_id(db, cast(int, assignment.teacher_id))
        if teacher_resource is not None and getattr(teacher_resource, "uuid", None):
            allocate.append(cast(str, teacher_resource.uuid))

        allocate = list(dict.fromkeys(allocate))

        appointments: list[SchemaRaplaApointment] = []
        current_date = cast(date, semester.data_rozpoczecia)
        end_date = cast(date, semester.data_zakonczenia)
        if end_date < current_date:
            continue

        weeks_count = ((end_date - current_date).days // 7) + 1
        total_minutes = cast(int, assignment.hours) * 60
        minutes_per_appointment = max(1, int(round(total_minutes / weeks_count)))
        start_time_value = datetime(2000, 1, 1, 7, 0, 0)
        end_time = (start_time_value + timedelta(minutes=minutes_per_appointment)).time().strftime("%H:%M:%S")
        while current_date <= end_date:
            appointments.append(
                SchemaRaplaApointment(
                    uuid=str(uuid4()),
                    start_date=format_rapla_date(current_date),
                    start_time=start_time,
                    end_date=format_rapla_date(current_date),
                    end_time=end_time,
                    allocate=allocate,
                )
            )
            current_date = current_date + timedelta(days=7)

        name_value = "Zajencia"
        if subject_resource is not None and getattr(subject_resource, "uuid", None):
            name_value = cast(str, subject_resource.uuid)
        elif assignment.subject is not None:
            name_value = cast(str, assignment.subject.name)

        reservation = reservations_by_key.get(name_value)
        if reservation is None:
            permissions = [
                RaplaPermission(
                    group="category[key='read-events-from-others']",
                    access="read",
                )
            ]

            field_of_study = None
            if assignment.subject_for_field_of_study is not None and getattr(
                assignment.subject_for_field_of_study, "field_of_study", None
            ) is not None:
                field_of_study = assignment.subject_for_field_of_study.field_of_study
            elif getattr(assignment, "subject_id", None) is not None:
                field_of_study = get_primary_field_of_study_for_subject(
                    db, cast(int, assignment.subject_id)
                )

            if field_of_study is not None:
                departments = get_departments_for_field_of_study(
                    db, cast(int, getattr(field_of_study, "id", None))
                ) or []
                seen: set[str] = set()
                for dept in departments:
                    abbr = getattr(dept, "abbreviation", None)
                    if not abbr:
                        continue
                    group = f"category[key='{abbr}_Editor']"
                    if group in seen:
                        continue
                    seen.add(group)
                    permissions.append(RaplaPermission(group=group, access="Edit"))

            reservation = SchemaRaplaReservationZajencia(
                uuid=str(uuid4()),
                owner=owner_uuid,
                created_at=created_at,
                last_changed=last_changed,
                last_changed_by=owner_uuid,
                appointments=appointments,
                name=name_value,
                permissions=permissions,
            )
            reservations_by_key[name_value] = reservation
        else:
            reservation.appointments.extend(appointments)

    return list(reservations_by_key.values())
