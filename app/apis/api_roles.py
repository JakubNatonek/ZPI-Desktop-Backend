from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_department_role import create_role, get_roles
from app.dependencies.auth import require_admin
from app.models.model_user import User
from app.schemas.role import RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dodaj nową rolę",
)
def create_role_entry(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> RoleResponse:
    try:
        role = create_role(db, payload.name.strip())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RoleResponse(id=role.id, name=role.name)


@router.get(
    "",
    response_model=List[RoleResponse],
    summary="Lista dostępnych ról",
)
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> List[RoleResponse]:
    roles = get_roles(db)
    return [RoleResponse(id=role.id, name=role.name) for role in roles]
