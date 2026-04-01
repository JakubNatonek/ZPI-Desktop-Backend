from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_department_role import create_department, get_departments
from app.dependencies.auth import require_admin
from app.models.model_user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse

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
    _: User = Depends(require_admin),
) -> DepartmentResponse:
    try:
        department = create_department(db, payload.name.strip())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return DepartmentResponse(id=department.id, name=department.name)


@router.get(
    "",
    response_model=List[DepartmentResponse],
    summary="Lista dostępnych wydziałów",
)
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> List[DepartmentResponse]:
    departments = get_departments(db)
    return [DepartmentResponse(id=department.id, name=department.name) for department in departments]
