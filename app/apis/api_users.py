from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import (
    create_user_by_admin,
    delete_user_by_admin,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    get_user_by_login,
    set_user_one_time_password,
    update_user_by_admin,
)
from app.cruds.crud_department_role import create_department, create_role, get_departments, get_roles
from app.schemas.user import (
    AdminResetOneTimePasswordRequest,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserUpdate,
    DepartmentOptionResponse,
    RoleOptionResponse,
    UserCreatedResponse,
    UserCredentialsResponse,
    UserNameResponse,
)
from app.schemas.department_role import DepartmentCreate, RoleCreate, DepartmentResponse, RoleResponse
from app.auth.current_user import get_current_user
from app.models.model_user import User

router = APIRouter(prefix="/users", tags=["users"])


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    role_value = current_user.role.name if current_user.role else str(current_user.role)
    if role_value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user


# Endpoint to add a department
@router.post("/add-department", response_model=DepartmentResponse, summary="Add a new department")
def add_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> DepartmentResponse:
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
    _: User = Depends(_require_admin),
) -> RoleResponse:
    try:
        r = create_role(db, role.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RoleResponse(id=r.id, name=r.name)


@router.get(
    "/roles",
    response_model=List[RoleOptionResponse],
    summary="Pobierz listę ról",
)
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> List[RoleOptionResponse]:
    roles = get_roles(db)
    return [RoleOptionResponse(id=role.id, name=role.name) for role in roles]


@router.get(
    "/departments",
    response_model=List[DepartmentOptionResponse],
    summary="Pobierz listę wydziałów",
)
def list_departments(
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> List[DepartmentOptionResponse]:
    departments = get_departments(db)
    return [DepartmentOptionResponse(id=department.id, name=department.name) for department in departments]


@router.post(
    "/admin-create",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz nowego użytkownika przez administratora",
)
def create_user_as_admin(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> UserCreatedResponse:
    normalized_email = str(payload.email).strip().lower()

    if get_user_by_email(db, normalized_email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    try:
        user = create_user_by_admin(
            db,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=normalized_email,
            one_time_password=payload.one_time_password,
            role_name=payload.role.strip(),
            department_name=payload.department.strip(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserCreatedResponse(
        user_id=user.user_id,
        album_number=user.album_number,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.name if user.role else None,
        department=user.department.name if user.department else None,
        one_time_password=user.plain_password,
    )

@router.get(
    "",
    response_model=List[UserNameResponse],
    summary="Pobierz listę użytkowników (imię, nazwisko, user_id)",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[UserNameResponse]:
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
    "/admin-list",
    response_model=List[AdminUserListResponse],
    summary="Lista użytkowników do zarządzania przez administratora",
)
def admin_list_users(
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> List[AdminUserListResponse]:
    users = get_all_users(db)
    return [
        AdminUserListResponse(
            user_id=user.user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            album_number=user.album_number,
            login=user.login,
            email=user.email,
            role=user.role.name if user.role else "",
            department=user.department.name if user.department else "",
            must_change_password=bool(user.must_change_password),
        )
        for user in users
    ]


@router.put(
    "/{user_id}",
    response_model=AdminUserListResponse,
    summary="Edytuj dane użytkownika",
)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_admin),
) -> AdminUserListResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    normalized_login = payload.login.strip().lower()
    normalized_email = str(payload.email).strip().lower()

    existing_login = get_user_by_login(db, normalized_login)
    if existing_login is not None and existing_login.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this login already exists")

    existing_email = get_user_by_email(db, normalized_email)
    if existing_email is not None and existing_email.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    role = next((role for role in get_roles(db) if role.name == payload.role.strip()), None)
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role not found: {payload.role}")

    department = next((department for department in get_departments(db) if department.name == payload.department.strip()), None)
    if department is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Department not found: {payload.department}")

    if current_user.user_id == user.user_id and role.name != "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin role")

    updated = update_user_by_admin(
        db,
        user=user,
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        login=normalized_login,
        email=normalized_email,
        role=role,
        department=department,
    )

    return AdminUserListResponse(
        user_id=updated.user_id,
        first_name=updated.first_name,
        last_name=updated.last_name,
        album_number=updated.album_number,
        login=updated.login,
        email=updated.email,
        role=updated.role.name if updated.role else "",
        department=updated.department.name if updated.department else "",
        must_change_password=bool(updated.must_change_password),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Usuń użytkownika",
)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_admin),
) -> None:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.user_id == user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")

    delete_user_by_admin(db, user)


@router.post(
    "/{user_id}/reset-one-time-password",
    response_model=UserCredentialsResponse,
    summary="Resetuj hasło użytkownika na jednorazowe",
)
def admin_reset_one_time_password(
    user_id: int,
    payload: AdminResetOneTimePasswordRequest,
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
) -> UserCredentialsResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated = set_user_one_time_password(db, user, payload.one_time_password)
    return UserCredentialsResponse(
        user_id=updated.user_id,
        login=updated.login,
        one_time_password=updated.plain_password or payload.one_time_password,
    )


