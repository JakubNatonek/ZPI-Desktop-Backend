from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_department import create_department, get_all_departments
from app.dependencies.auth import require_admin
from app.models.model_user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["departments"])

# NOTE: Frontend need fix cos sends incorect data
@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nowy wydział",
)
def create_department_entry(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
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

# NOTE: Frontend need fix cos recive incorect data
@router.get(
    "/list",
    response_model=list[DepartmentResponse],
    summary="Lista dostępnych wydziałów",
)
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[DepartmentResponse]:
    departments = get_all_departments(db)
    return [DepartmentResponse(id = cast(int, department.id), name = cast(str, department.name), abbreviation = cast(str, department.abbreviation)) for department in departments]
