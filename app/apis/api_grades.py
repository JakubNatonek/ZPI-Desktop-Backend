from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.cruds.crud_grade import (
    admin_replace_subject_grades,
    get_current_semester,
    get_lecturer_semester_grades,
    get_student_grades_by_album,
    get_student_semester_grades,
    list_semester_options,
    replace_subject_grades,
)
from app.models.model_user import User
from app.schemas.grade import (
    AdminSubjectGradeUpdateRequest,
    LecturerSemesterGradesResponse,
    SemesterOptionResponse,
    SemesterGradesResponse,
    SubjectGradeUpdateRequest,
)


router = APIRouter(prefix="/grades", tags=["grades"])

LECTURER_ROLE_NAMES = {"lecturer", "wykladowca", "wykładowca", "cwiczenia", "ćwiczenia", "laboratorium", "seminarium"}
STUDENT_ROLE_NAMES = {"student"}
ADMIN_ROLE_NAMES = {"admin"}


def _is_lecturer(user: User) -> bool:
    return user_has_role(user, LECTURER_ROLE_NAMES)


def _is_student(user: User) -> bool:
    return user_has_role(user, STUDENT_ROLE_NAMES)


def _is_admin(user: User) -> bool:
    return user_has_role(user, ADMIN_ROLE_NAMES)


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
    summary="Pobierz oceny dla zalogowanego wykladowcy (wszystkie semestry)",
)
def get_lecturer_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LecturerSemesterGradesResponse]:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can view this endpoint")

    return get_lecturer_semester_grades(db, current_user.user_id, current_only=False)


@router.get(
    "/semesters",
    response_model=list[SemesterOptionResponse],
    summary="Pobierz listę semestrów do filtrowania ocen",
)
def get_semester_options(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SemesterOptionResponse]:
    if not (_is_admin(current_user) or _is_lecturer(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and lecturers can view this endpoint")

    return list_semester_options(db)


@router.put(
    "/lecturer/subject",
    response_model=dict[str, str],
    summary="Zastap komplet ocen dla wybranego przedmiotu i studenta (bieżący semestr)",
)
def update_lecturer_subject_grades(
    payload: SubjectGradeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not _is_lecturer(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can edit grades")

    current_semester = get_current_semester(db)
    if current_semester is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brak zdefiniowanych semestrow. Edycja ocen jest tymczasowo niedostepna.",
        )

    if payload.semester != current_semester.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wykladowca moze wystawiac i edytowac oceny tylko w najnowszym semestrze.",
        )

    try:
        final_grade = _parse_grade(payload.final_grade)
        partial_grades = [
            {
                "label": partial.label,
                "info": partial.info,
                "grade": _parse_grade(partial.grade),
                "weight": partial.weight,
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
            subject_weight=payload.subject_weight,
            partial_grades=partial_grades,
            allow_subject_weight_edit=False,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "Grades updated"}


@router.get(
    "/admin/{album_number}",
    response_model=dict,
    summary="Admin: pobierz oceny studenta po numerze albumu",
)
def admin_get_student_grades(
    album_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view this endpoint")

    try:
        semesters, student_info = get_student_grades_by_album(db, album_number.strip())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {
        "student": student_info,
        "semesters": [s.model_dump() for s in semesters],
    }


@router.put(
    "/admin/subject",
    response_model=dict[str, str],
    summary="Admin: edytuj oceny dowolnego studenta",
)
def admin_update_subject_grades(
    payload: AdminSubjectGradeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can edit grades")

    try:
        final_grade = _parse_grade(payload.final_grade)
        partial_grades = [
            {
                "label": partial.label,
                "info": partial.info,
                "grade": _parse_grade(partial.grade),
                "weight": partial.weight,
            }
            for partial in payload.partial_grades
        ]

        admin_replace_subject_grades(
            db=db,
            lecturer_id=payload.lecturer_id,
            student_id=payload.student_id,
            semester=payload.semester,
            subject_name=payload.subject.strip(),
            final_grade=final_grade,
            subject_weight=payload.subject_weight,
            partial_grades=partial_grades,
            fallback_lecturer_id=current_user.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "Grades updated by admin"}
