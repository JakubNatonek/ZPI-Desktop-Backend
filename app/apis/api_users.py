from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, get_user_role_names
from app.core.database import get_db
from app.cruds.crud_user import (
    create_user_by_admin,
    delete_user_by_admin,
    get_all_users,
    get_related_names_for_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_login,
    set_user_password,
    update_user_by_admin,
)
from app.cruds.crud_title import list_titles
from app.cruds.crud_title_for_user import list_titles_for_user
from app.cruds.crud_departments_for_user import get_departments_for_user
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.dependencies.auth import require_role
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
    TitleOptionResponse,
    UserCreatedResponse,
    UserNameResponse,
    UserProfileResponse,
    CurrentUserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])

USER_NOT_FOUND_DETAIL = "User not found"
USER_NOT_EXIST_DETAIL = "User does not exist."
USER_EMAIL_EXISTS_DETAIL = "User with this email already exists"
USER_LOGIN_EXISTS_DETAIL = "User with this login already exists"


def _normalize_credential(value: str) -> str:
    return str(value).strip().lower()


def _get_user_or_404(db: Session, user_id: int, detail: str = USER_NOT_FOUND_DETAIL) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return user


def _build_admin_user_list_item(db: Session, user: User) -> AdminUserListResponse:
    return AdminUserListResponse(
        user_id=user.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        album_number=user.album_number,
        login=user.login,
        email=user.email,
        titles=get_related_names_for_user(db, user.user_id, list_titles_for_user),
        roles=get_related_names_for_user(db, user.user_id, get_roles_for_user),
        departments=get_related_names_for_user(db, user.user_id, get_departments_for_user),
        must_change_password=bool(user.must_change_password),
    )


def _build_user_name_response(user: User) -> UserNameResponse:
    return UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name)


def _status_for_user_validation_error(detail: str) -> int:
    normalized = detail.strip().lower()
    if "already exists" in normalized or "cannot be deleted" in normalized or "constraint" in normalized:
        return status.HTTP_409_CONFLICT
    return status.HTTP_400_BAD_REQUEST


@router.post(
    "/create",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Utwórz nowego użytkownika przez administratora",
)
def create_user_as_admin(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
) -> UserCreatedResponse:
    normalized_email = _normalize_credential(payload.email)

    if get_user_by_email(db, normalized_email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_EMAIL_EXISTS_DETAIL)

    try:
        user = create_user_by_admin(
            db,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=normalized_email,
            password=payload.password,
            role_ids=payload.role_ids,
            department_ids=payload.department_ids,
            title_ids=payload.title_ids,
            admin=admin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=_status_for_user_validation_error(str(exc)), detail=str(exc)) from exc

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
    return [_build_user_name_response(user) for user in users]


@router.get(
    "/titles/list",
    response_model=List[TitleOptionResponse],
    summary="Lista dostępnych tytułów naukowych",
)
def list_user_title_options(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> List[TitleOptionResponse]:
    titles = list_titles(db)
    return [TitleOptionResponse(id=title.id, name=title.name) for title in titles]

# NOTE: Double user usage?
@router.get(
    "/{user_id}/name",
    response_model=UserNameResponse,
    summary="Pobierz imię i nazwisko użytkownika po user_id",
)
def get_user_name(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> UserNameResponse:
    user = _get_user_or_404(db, user_id, USER_NOT_EXIST_DETAIL)
    return _build_user_name_response(user)

# NOTE: Double user usage?
@router.get(
    "/{user_id}/public-key",
    response_model=PublicKeyResponse,
    summary="Pobierz klucz publiczny użytkownika",
)
def get_user_public_key(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PublicKeyResponse:
    user = _get_user_or_404(db, user_id, USER_NOT_EXIST_DETAIL)
    return PublicKeyResponse(user_id=user.user_id, public_key=getattr(user, "public_key", None))

# NOTE: Double user usage?
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update public key for other user")
    user = _get_user_or_404(db, user_id, USER_NOT_EXIST_DETAIL)
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
    return [_build_admin_user_list_item(db, user) for user in users]


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
    user = _get_user_or_404(db, user_id)

    normalized_login = _normalize_credential(payload.login)
    normalized_email = _normalize_credential(payload.email)

    existing_login = get_user_by_login(db, normalized_login)
    if existing_login is not None and existing_login.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_LOGIN_EXISTS_DETAIL)

    existing_email = get_user_by_email(db, normalized_email)
    if existing_email is not None and existing_email.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_EMAIL_EXISTS_DETAIL)

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
        raise HTTPException(status_code=_status_for_user_validation_error(str(exc)), detail=str(exc)) from exc

    return _build_admin_user_list_item(db, updated)


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
    user = _get_user_or_404(db, user_id)

    if current_user.user_id == user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")

    try:
        delete_user_by_admin(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=_status_for_user_validation_error(str(exc)), detail=str(exc)) from exc


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
    user = _get_user_or_404(db, user_id)

    set_user_password(db, user, payload.password)
    return ChangePasswordResponse(message="Password reset successfully")


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Pobierz profil zalogowanego użytkownika",
)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    role_names = get_user_role_names(current_user)
    student_profile = current_user.student_profile
    teacher_profile = current_user.teacher_profile
    department = current_user.department
    group = student_profile.group if student_profile else None
    group_code = group.code if group else None
    is_student = "student" in role_names

    if is_student:
        status = "Aktywny student"
    elif role_names.intersection({"wykladowca", "lecturer"}):
        status = "Pracownik dydaktyczny"
    elif role_names.intersection({"planista", "planner"}):
        status = "Planista"
    else:
        status = "Administrator systemu"

    return UserProfileResponse(
        status=status,
        album_number=student_profile.index_number if student_profile and student_profile.index_number else "Nie dotyczy",
        year=str(group.year) if group else "Nie dotyczy",
        semester=str(student_profile.semester) if student_profile and student_profile.semester is not None else "Nie dotyczy",
        major=department.name if department else "Nie dotyczy",
        faculty=department.name if department else "Nie dotyczy",
        study_track="Ogolnoakademicki" if is_student else "Nie dotyczy",
        study_mode="Stacjonarne" if is_student else "Nie dotyczy",
        title=teacher_profile.title if teacher_profile and teacher_profile.title else "Nie dotyczy",
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


