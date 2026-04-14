from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import delete_user_by_admin, get_user_by_id
from app.cruds.crud_lecturer_management import get_lecturers, set_lecturer_blocked, update_lecturer_data
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.lecturer_management import LecturerBlockRequest, LecturerListItemResponse, LecturerUpdateRequest

router = APIRouter(prefix="/admin/lecturers", tags=["lecturer-management"])


@router.get(
    "/list",
    response_model=list[LecturerListItemResponse],
    summary="Lista wykładowców z możliwością filtrowania po kierunku",
)
def list_lecturers(
    department_id: int | None = Query(None, description="Filtruj po ID kierunku (departamentu)"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[LecturerListItemResponse]:
    lecturers = get_lecturers(db, department_id)
    return [LecturerListItemResponse(**l) for l in lecturers]


@router.patch(
    "/{user_id}/block",
    response_model=LecturerListItemResponse,
    summary="Zablokuj lub odblokuj konto wykładowcy",
)
def toggle_lecturer_block(
    user_id: int,
    payload: LecturerBlockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> LecturerListItemResponse:
    if current_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nie możesz zablokować własnego konta")

    user = set_lecturer_blocked(db, user_id, payload.blocked)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wykładowca nie znaleziony")

    lecturers = get_lecturers(db)
    lecturer_data = next((l for l in lecturers if l["user_id"] == user_id), None)
    if lecturer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wykładowca nie znaleziony")
    return LecturerListItemResponse(**lecturer_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń konto wykładowcy",
)
def delete_lecturer(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> None:
    if current_user.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nie możesz usunąć własnego konta")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wykładowca nie znaleziony")

    delete_user_by_admin(db, user)


@router.put(
    "/{user_id}",
    response_model=LecturerListItemResponse,
    summary="Edytuj dane wykładowcy",
)
def edit_lecturer(
    user_id: int,
    payload: LecturerUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> LecturerListItemResponse:
    existing_email = db.query(User).filter(User.email == payload.email.strip().lower(), User.user_id != user_id).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Użytkownik z tym adresem email już istnieje")

    user = update_lecturer_data(
        db, user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        title=payload.title,
        department_id=payload.department_id,
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wykładowca nie znaleziony")

    lecturers = get_lecturers(db)
    lecturer_data = next((l for l in lecturers if l["user_id"] == user_id), None)
    if lecturer_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wykładowca nie znaleziony")
    return LecturerListItemResponse(**lecturer_data)
