from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_grade import delete_subject_grades, get_lecturer_semester_grades, get_student_semester_grades, replace_subject_grades
from app.models.model_user import User
from app.seed_data.seed_model.seed_roles import RolaEnum
from app.schemas.grade import LecturerSemesterGradesResponse, SemesterGradesResponse, SubjectGradeDeleteRequest, SubjectGradeUpdateRequest


router = APIRouter(prefix="/grades", tags=["grades"])

LECTURER_ROLE_NAMES = {
    RolaEnum.WYKLADOWCA.value,
}
STUDENT_ROLE_NAMES = {RolaEnum.STUDENT.value}
MIN_GRADE_VALUE = 2.0
MAX_GRADE_VALUE = 5.0


@dataclass(frozen=True)
class AccessContext:
    user: User
    is_lecturer: bool
    is_student: bool


def _resolve_access_context(
    current_user: User = Depends(get_current_user),
) -> AccessContext:
    return AccessContext(
        user=current_user,
        is_lecturer=user_has_role(current_user, LECTURER_ROLE_NAMES),
        is_student=user_has_role(current_user, STUDENT_ROLE_NAMES),
    )


def _require_student(access: AccessContext = Depends(_resolve_access_context)) -> User:
    if not access.is_student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view this endpoint")
    return access.user


def _require_lecturer(access: AccessContext = Depends(_resolve_access_context)) -> User:
    if not access.is_lecturer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can access this endpoint")
    return access.user


def _parse_grade(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    parsed = float(normalized)
    if parsed < MIN_GRADE_VALUE or parsed > MAX_GRADE_VALUE:
        raise ValueError(f"Grade value must be between {MIN_GRADE_VALUE} and {MAX_GRADE_VALUE}")
    return parsed


def _normalize_subject(subject: str) -> str:
    normalized = subject.strip()
    if not normalized:
        raise ValueError("Subject cannot be empty")
    return normalized


@router.get(
    "/me",
    response_model=list[SemesterGradesResponse],
    summary="Pobierz oceny zalogowanego studenta",
)
def get_my_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
) -> list[SemesterGradesResponse]:
    return get_student_semester_grades(db, current_user.user_id)


@router.get(
    "/lecturer/me",
    response_model=list[LecturerSemesterGradesResponse],
    summary="Pobierz oceny przypisane do zalogowanego wykladowcy",
)
def get_lecturer_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer),
) -> list[LecturerSemesterGradesResponse]:
    return get_lecturer_semester_grades(db, current_user.user_id)


@router.put(
    "/lecturer/subject",
    response_model=dict[str, str],
    summary="Zastap komplet ocen dla wybranego przedmiotu i studenta",
)
def update_lecturer_subject_grades(
    payload: SubjectGradeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer),
) -> dict[str, str]:
    try:
        normalized_subject = _normalize_subject(payload.subject)
        final_grade = _parse_grade(payload.final_grade)
        partial_grades = [
            {
                "label": partial.label,
                "info": partial.info,
                "grade": _parse_grade(partial.grade),
            }
            for partial in payload.partial_grades
        ]

        replace_subject_grades(
            db=db,
            lecturer_id=current_user.user_id,
            student_id=payload.student_id,
            semester=payload.semester,
            subject_name=normalized_subject,
            final_grade=final_grade,
            partial_grades=partial_grades,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "Grades updated"}


@router.delete(
    "/lecturer/subject",
    response_model=dict[str, str],
    summary="Usun komplet ocen dla wybranego przedmiotu i studenta",
)
def delete_lecturer_subject_grades(
    payload: SubjectGradeDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer),
) -> dict[str, str]:
    try:
        normalized_subject = _normalize_subject(payload.subject)
        deleted_count = delete_subject_grades(
            db=db,
            lecturer_id=current_user.user_id,
            student_id=payload.student_id,
            semester=payload.semester,
            subject_name=normalized_subject,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grades not found")

    return {"message": "Grades deleted"}
