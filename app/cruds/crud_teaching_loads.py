from sqlalchemy.orm import Session, joinedload

from app.models.model_teaching_load import TeachingLoadAssignment
from app.models.model_user import User
from app.models.model_subject import Subject
from app.models.model_activity import Activity
from app.models.model_semestr import Semestr
from app.models.model_title_for_user import TitleForUser
from app.models.model_title import TitleModel
from app.schemas.teaching_load import TeachingLoadAssignmentDto, TeachingLoadCreatePayload, TeachingLoadPatchPayload


def _build_dto(assignment: TeachingLoadAssignment) -> TeachingLoadAssignmentDto:
    teacher: User | None = assignment.teacher
    subject: Subject | None = assignment.subject
    activity: Activity | None = assignment.activity
    semester: Semestr | None = assignment.semester

    teacher_title: str | None = None
    if teacher and teacher.title_assignments:
        first_ta = teacher.title_assignments[0]
        if hasattr(first_ta, "title") and first_ta.title:
            teacher_title = first_ta.title.name

    return TeachingLoadAssignmentDto(
        id=assignment.id,
        teacher_id=assignment.teacher_id,
        teacher_title=teacher_title,
        teacher_first_name=teacher.first_name if teacher else None,
        teacher_last_name=teacher.last_name if teacher else None,
        subject_id=assignment.subject_id,
        subject_name=subject.name if subject else None,
        activity_id=assignment.activity_id,
        activity_name=activity.name if activity else None,
        semester_id=assignment.semester_id,
        semester_name=semester.nazwa if semester else None,
        hours=assignment.hours,
    )


def _load_options():
    return [
        joinedload(TeachingLoadAssignment.teacher).joinedload(User.title_assignments).joinedload(TitleForUser.title),
        joinedload(TeachingLoadAssignment.subject),
        joinedload(TeachingLoadAssignment.activity),
        joinedload(TeachingLoadAssignment.semester),
    ]


def get_all_teaching_loads(db: Session) -> list[TeachingLoadAssignmentDto]:
    rows = db.query(TeachingLoadAssignment).options(*_load_options()).all()
    return [_build_dto(row) for row in rows]


def get_teaching_load_by_id(db: Session, assignment_id: int) -> TeachingLoadAssignment | None:
    return db.query(TeachingLoadAssignment).options(*_load_options()).filter(
        TeachingLoadAssignment.id == assignment_id
    ).first()


def create_teaching_load(db: Session, payload: TeachingLoadCreatePayload) -> TeachingLoadAssignmentDto:
    assignment = TeachingLoadAssignment(
        teacher_id=payload.teacher_id,
        subject_id=payload.subject_id,
        activity_id=payload.activity_id,
        semester_id=payload.semester_id,
        hours=payload.hours,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    row = get_teaching_load_by_id(db, assignment.id)
    return _build_dto(row)  # type: ignore[arg-type]


def patch_teaching_load(db: Session, assignment_id: int, payload: TeachingLoadPatchPayload) -> TeachingLoadAssignmentDto | None:
    assignment = db.query(TeachingLoadAssignment).filter(TeachingLoadAssignment.id == assignment_id).first()
    if not assignment:
        return None

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(assignment, field, value)
    db.commit()

    row = get_teaching_load_by_id(db, assignment_id)
    return _build_dto(row)  # type: ignore[arg-type]


def delete_teaching_load(db: Session, assignment_id: int) -> bool:
    assignment = db.query(TeachingLoadAssignment).filter(TeachingLoadAssignment.id == assignment_id).first()
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True
