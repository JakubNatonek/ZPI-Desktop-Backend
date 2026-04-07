from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_grade import get_lecturer_semester_grades, get_student_semester_grades, replace_subject_grades
from app.models.model_user import User
from app.schemas.grade import LecturerSemesterGradesResponse, SemesterGradesResponse, SubjectGradeUpdateRequest


router = APIRouter(prefix="/grades", tags=["grades"])

# NOTE: Static data for what ?
LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "cwiczenia", "laboratorium", "seminarium"}
STUDENT_ROLE_NAMES = {"student"}


def _is_lecturer(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in LECTURER_ROLE_NAMES


def _is_student(user: User) -> bool:
    role_name = (user.role.name if user.role else "").strip().lower()
    return role_name in STUDENT_ROLE_NAMES


def _parse_grade(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    parsed = float(normalized)
    if parsed < 2.0 or parsed > 5.0:
        raise ValueError("Grade value must be between 2.0 and 5.0")
    return parsed


@router.get(
    "/me",
    response_model=list[SemesterGradesResponse],
    summary="Pobierz oceny zalogowanego studenta",
)
def get_my_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SemesterGradesResponse]:
    if not _is_student(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view this endpoint")

    return get_student_semester_grades(db, current_user.user_id)


@router.get(
    "/lecturer/me",
    response_model=list[LecturerSemesterGradesResponse],
    summary="Pobierz oceny przypisane do zalogowanego wykladowcy",
)
def get_lecturer_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LecturerSemesterGradesResponse]:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can view this endpoint")

    return get_lecturer_semester_grades(db, current_user.user_id)


@router.put(
    "/lecturer/subject",
    response_model=dict[str, str],
    summary="Zastap komplet ocen dla wybranego przedmiotu i studenta",
)
def update_lecturer_subject_grades(
    payload: SubjectGradeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can edit grades")

    try:
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
            subject_name=payload.subject.strip(),
            final_grade=final_grade,
            partial_grades=partial_grades,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "Grades updated"}
