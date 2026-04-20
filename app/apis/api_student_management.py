from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import delete_user_by_admin, get_user_by_id
from app.cruds.crud_student_management import get_students_by_department, set_user_blocked, update_student_data
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.student_management import StudentBlockRequest, StudentListItemResponse, StudentUpdateRequest

router = APIRouter(prefix="/admin/students", tags=["student-management"])


@router.get(
    "/list",
    response_model=list[StudentListItemResponse],
    summary="Lista studentów z możliwością filtrowania po kierunku",
)
def list_students(
    department_id: int | None = Query(None, description="Filtruj po ID kierunku (departamentu)"),
    studies_type: str | None = Query(None, description="Filtruj po typie studiów (stacjonarne / niestacjonarne)"),
    specialization_id: int | None = Query(None, description="Filtruj po ID kierunku/specjalności"),
    semester_id: int | None = Query(None, description="Filtruj studentów mających oceny w podanym semestrze"),
    album_query: str | None = Query(None, description="Szukaj po fragmencie numeru albumu"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[StudentListItemResponse]:
    students = get_students_by_department(
        db,
        department_id=department_id,
        studies_type=studies_type,
        specialization_id=specialization_id,
        semester_id=semester_id,
        album_query=album_query,
    )
    return [StudentListItemResponse(**s) for s in students]


@router.patch(
    "/{user_id}/block",
    response_model=StudentListItemResponse,
    summary="Zablokuj lub odblokuj konto studenta",
)
def toggle_student_block(
    user_id: int,
    payload: StudentBlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> StudentListItemResponse:
    if current_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nie możesz zablokować własnego konta")

    user = set_user_blocked(db, user_id, payload.blocked)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student nie znaleziony")

    # Re-fetch via list to get full student data
    students = get_students_by_department(db)
    student_data = next((s for s in students if s["user_id"] == user_id), None)
    if student_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student nie znaleziony")
    return StudentListItemResponse(**student_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń konto studenta",
)
def delete_student(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> None:
    if current_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nie możesz usunąć własnego konta")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student nie znaleziony")

    delete_user_by_admin(db, user)


@router.put(
    "/{user_id}",
    response_model=StudentListItemResponse,
    summary="Edytuj dane studenta",
)
def edit_student(
    user_id: int,
    payload: StudentUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> StudentListItemResponse:
    # Check uniqueness of email and album_number
    existing_email = db.query(User).filter(User.email == payload.email.strip().lower(), User.user_id != user_id).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Użytkownik z tym adresem email już istnieje")

    existing_album = db.query(User).filter(User.album_number == payload.album_number.strip(), User.user_id != user_id).first()
    if existing_album:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Użytkownik z tym numerem albumu już istnieje")

    user = update_student_data(
        db, user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        album_number=payload.album_number,
        department_id=payload.department_id,
        studies_type=payload.studies_type,
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student nie znaleziony")

    students = get_students_by_department(db)
    student_data = next((s for s in students if s["user_id"] == user_id), None)
    if student_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student nie znaleziony")
    return StudentListItemResponse(**student_data)
