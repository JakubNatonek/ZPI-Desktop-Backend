from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_role import create_role, get_role_by_id, get_roles
from app.dependencies.auth import require_role
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
    _: User = Depends(require_role("admin")),
) -> RoleResponse:
    try:
        role = create_role(db, payload.name.strip())
    except ValueError as exc:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(exc)
            ) from exc
    return RoleResponse(
            id = cast(int, role.id),
            name = cast(str, role.name),
        )


@router.get(
    "/list",
    response_model=List[RoleResponse],
    summary="Lista dostępnych ról",
)
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> List[RoleResponse]:
    roles = get_roles(db)
    return [RoleResponse(id = cast(int, role.id), name = cast(str, role.name),) for role in roles]


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń rolę",
)
def delete_role_entry(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    role = get_role_by_id(db, role_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    db.delete(role)
    db.commit()
