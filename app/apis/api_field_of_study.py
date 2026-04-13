from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_department import (
    create_department,
    delete_department,
    get_all_departments,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.field_of_study import FieldOfStudyCreate, FieldOfStudyResponse

router = APIRouter(prefix="/field-of-study", tags=["field-of-study"])


@router.get(
    "/list",
    response_model=list[FieldOfStudyResponse],
    summary="Lista kierunków studiów",
)
def list_fields_of_study(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[FieldOfStudyResponse]:
    departments = get_all_departments(db)
    return [
        FieldOfStudyResponse(
            id=cast(int, d.id),
            code=cast(str, d.abbreviation),
            name=cast(str, d.name),
        )
        for d in departments
    ]


@router.post(
    "",
    response_model=FieldOfStudyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nowy kierunek studiów",
)
def create_field_of_study_entry(
    payload: FieldOfStudyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> FieldOfStudyResponse:
    try:
        department = create_department(db, name=payload.name.strip(), abbreviation=payload.code.strip())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FieldOfStudyResponse(
        id=cast(int, department.id),
        code=cast(str, department.abbreviation),
        name=cast(str, department.name),
    )


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń kierunek studiów",
)
def delete_field_of_study_entry(
    field_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    if not delete_department(db, field_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kierunek nie został znaleziony.")
