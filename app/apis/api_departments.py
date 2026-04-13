from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_department import (
    create_department,
    delete_department,
    get_all_departments,
    get_department_by_id,
    update_department,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nowy wydział",
)
def create_department_entry(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> DepartmentResponse:
    try:
        department = create_department(db = db, name = payload.name.strip(), abbreviation = payload.abbreviation.strip())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DepartmentResponse(
            id = cast(int, department.id), 
            name = cast(str, department.name), 
            abbreviation = cast(str, department.abbreviation)
        )


@router.get(
    "/list",
    response_model=list[DepartmentResponse],
    summary="Lista dostępnych wydziałów",
)
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> list[DepartmentResponse]:
    departments = get_all_departments(db)
    return [DepartmentResponse(id = cast(int, department.id), name = cast(str, department.name), abbreviation = cast(str, department.abbreviation)) for department in departments]


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Szczegóły wydziału",
)
def get_department_entry(
    department_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> DepartmentResponse:
    department = get_department_by_id(db, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    return DepartmentResponse(
        id=cast(int, department.id),
        name=cast(str, department.name),
        abbreviation=cast(str, department.abbreviation),
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Edytuj wydział",
)
def update_department_entry(
    department_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> DepartmentResponse:
    try:
        department = update_department(
            db,
            department_id=department_id,
            name=payload.name.strip(),
            abbreviation=payload.abbreviation.strip(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    return DepartmentResponse(
        id=cast(int, department.id),
        name=cast(str, department.name),
        abbreviation=cast(str, department.abbreviation),
    )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń wydział",
)
def delete_department_entry(
    department_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    deleted = delete_department(db, department_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
