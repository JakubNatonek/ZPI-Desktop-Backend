from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_specialization import (
    create_specialization,
    delete_specialization,
    get_all_specializations,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.specialization import SpecializationCreate, SpecializationResponse

router = APIRouter(prefix="/specializations", tags=["specializations"])


def _to_response(group) -> SpecializationResponse:
    return SpecializationResponse(
        id=cast(int, group.id),
        code=cast(str, group.code),
        name=cast(str, group.specialization),
        department_id=group.department_id,
        department_name=group.department.name if group.department else "",
    )


@router.get(
    "/list",
    response_model=list[SpecializationResponse],
    summary="Lista specjalności",
)
def list_specializations(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[SpecializationResponse]:
    groups = get_all_specializations(db)
    return [_to_response(g) for g in groups]


@router.post(
    "",
    response_model=SpecializationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nową specjalność",
)
def create_specialization_entry(
    payload: SpecializationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SpecializationResponse:
    try:
        group = create_specialization(
            db,
            code=payload.code.strip(),
            name=payload.name.strip(),
            department_id=payload.department_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # Reload with department relationship
    db.refresh(group)
    if group.department is None:
        from app.models.model_department import Department
        group.department = db.query(Department).filter(Department.id == group.department_id).first()
    return _to_response(group)


@router.delete(
    "/{spec_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń specjalność",
)
def delete_specialization_entry(
    spec_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    if not delete_specialization(db, spec_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specjalność nie została znaleziona.")
