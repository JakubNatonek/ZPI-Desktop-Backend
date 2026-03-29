from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import get_all_users, get_user_by_id
from app.cruds.crud_department_role import create_department, create_role
from app.schemas.user import UserNameResponse, PublicKeyResponse, PublicKeyUpdate
from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.schemas.role import RoleCreate, RoleResponse
from app.auth.current_user import get_current_user
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation

router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to add a department
@router.post("/add-department", response_model=DepartmentResponse, summary="Add a new department")
def add_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> DepartmentResponse:
    _ = current_user
    try:
        dep = create_department(db, department.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DepartmentResponse(id=dep.id, name=dep.name)


# Endpoint to add a role
@router.post("/add-role", response_model=RoleResponse, summary="Add a new role")
def add_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> RoleResponse:
    _ = current_user
    try:
        r = create_role(db, role.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RoleResponse(id=r.id, name=r.name)

@router.get(
    "",
    response_model=List[UserNameResponse],
    summary="Pobierz listę użytkowników (imię, nazwisko, user_id)",
)
def list_users(db: Session = Depends(get_db)) -> List[UserNameResponse]:
    users = get_all_users(db)
    return [UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name) for user in users]


@router.get(
    "/{user_id}/name",
    response_model=UserNameResponse,
    summary="Pobierz imię i nazwisko użytkownika po user_id",
)
def get_user_name(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> UserNameResponse:
    _ = current_user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist.")
    return UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name)


@router.get(
    "/{user_id}/public-key",
    response_model=PublicKeyResponse,
    summary="Pobierz klucz publiczny użytkownika",
)
def get_user_public_key(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> PublicKeyResponse:
    _ = current_user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist.")
    return PublicKeyResponse(user_id=user.user_id, public_key=getattr(user, "public_key", None))


@router.put(
    "/{user_id}/public-key",
    response_model=PublicKeyResponse,
    summary="Zaktualizuj klucz publiczny użytkownika",
)
def set_user_public_key(
    user_id: int,
    payload: PublicKeyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> PublicKeyResponse:
    # only allow users to update their own public key
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot update public key for other user")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist.")
    user.public_key = payload.public_key
    db.add(user)
    db.commit()
    db.refresh(user)
    return PublicKeyResponse(user_id=user.user_id, public_key=user.public_key)


