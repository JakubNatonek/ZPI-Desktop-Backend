from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_login import (
    create_user_by_admin,
    delete_user_by_admin,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    get_user_by_login,
    set_user_password,
    update_user_by_admin,
)
from app.cruds.crud_departments_for_user import get_departments_for_user
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_user import get_related_names_for_user
from app.dependencies.auth import require_role
from app.models.model_department import Department
from app.models.model_role import Role
from app.models.model_user import User
from app.schemas.user import (
    AdminResetPasswordRequest,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserUpdate,
    ChangePasswordResponse,
    PublicKeyResponse,
    PublicKeyUpdate,
    UserCreatedResponse,
    UserNameResponse,
    UserProfileResponse,
    CurrentUserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz nowego użytkownika przez administratora",
)
def create_user_as_admin(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
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
            password=payload.password,
            role_ids=payload.role_ids,
            department_ids=payload.department_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    roles = get_related_names_for_user(db, user.user_id, get_roles_for_user)
    departments = get_related_names_for_user(db, user.user_id, get_departments_for_user)

    return UserCreatedResponse(
        user_id=user.user_id,
        album_number=user.album_number,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=roles,
        departments=departments,
    )

@router.get(
    "/list",
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


@router.get(
    "/admin-list",
    response_model=List[AdminUserListResponse],
    summary="Lista użytkowników do zarządzania przez administratora",
)
def admin_list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
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
            roles=get_related_names_for_user(db, user.user_id, get_roles_for_user),
            departments=get_related_names_for_user(db, user.user_id, get_departments_for_user),
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
    current_user: User = Depends(require_role("admin")),
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

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin role not found")

    if current_user.user_id == user.user_id and admin_role.id not in payload.role_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin role")

    try:
        updated = update_user_by_admin(
            db,
            user=user,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            login=normalized_login,
            email=normalized_email,
            role_ids=payload.role_ids,
            department_ids=payload.department_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AdminUserListResponse(
        user_id=updated.user_id,
        first_name=updated.first_name,
        last_name=updated.last_name,
        album_number=updated.album_number,
        login=updated.login,
        email=updated.email,
        roles=get_related_names_for_user(db, updated.user_id, get_roles_for_user),
        departments=get_related_names_for_user(db, updated.user_id, get_departments_for_user),
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
    current_user: User = Depends(require_role("admin")),
) -> None:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.user_id == user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")

    delete_user_by_admin(db, user)


@router.post(
    "/{user_id}/reset-password",
    response_model=ChangePasswordResponse,
    summary="Resetuj hasło użytkownika",
)
def admin_reset_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> ChangePasswordResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    set_user_password(db, user, payload.password)
    return ChangePasswordResponse(message="Password reset successfully")


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Pobierz profil zalogowanego użytkownika",
)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    role_name = (current_user.role.name if current_user.role else "").lower()
    group_code = current_user.student_profile.group.code if current_user.student_profile and current_user.student_profile.group else None

    if role_name == "student":
        status = "Aktywny student"
    elif role_name in {"wykladowca", "lecturer"}:
        status = "Pracownik dydaktyczny"
    elif role_name in {"planista", "planner"}:
        status = "Planista"
    else:
        status = "Administrator systemu"

    return UserProfileResponse(
        status=status,
        album_number=current_user.student_profile.index_number if current_user.student_profile and current_user.student_profile.index_number else "Nie dotyczy",
        year=str(current_user.student_profile.group.year) if current_user.student_profile and current_user.student_profile.group else "Nie dotyczy",
        semester=str(current_user.student_profile.semester) if current_user.student_profile and current_user.student_profile.semester is not None else "Nie dotyczy",
        major=current_user.department.name if current_user.department else "Nie dotyczy",
        faculty=current_user.department.name if current_user.department else "Nie dotyczy",
        study_track="Ogolnoakademicki" if role_name == "student" else "Nie dotyczy",
        study_mode="Stacjonarne" if role_name == "student" else "Nie dotyczy",
        title=current_user.teacher_profile.title if current_user.teacher_profile and current_user.teacher_profile.title else "Nie dotyczy",
        groups=[group_code] if group_code else [],
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Dane zalogowanego użytkownika",
)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    role_names = [name.lower() for name in get_related_names_for_user(db, current_user.user_id, get_roles_for_user)]
    department_names = get_related_names_for_user(db, current_user.user_id, get_departments_for_user)
    return CurrentUserResponse(
        user_id=current_user.user_id,
        login=current_user.login,
        email=current_user.email,
        roles=role_names,
        departments=department_names,
    )


