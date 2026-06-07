from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, get_user_role_names
from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
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
from app.models.model_department import Department
from app.models.model_role import Role
from app.models.model_user import User
from app.schemas.user import (
    AdminResetPasswordRequest,
    AdminUserCreate,
    AdminUserListResponse,
    AdminUserUpdate,
    AvatarResponse,
    AvatarUpdateRequest,
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
    normalized_email = str(payload.email).strip().lower() # NOTE: DON'T do this this is bad chyba

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
            title_ids=payload.title_ids,
            admin=admin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=_status_for_user_validation_error(str(exc)), detail=str(exc)) from exc

    roles = get_related_names_for_user(db, user.user_id, get_roles_for_user)
    departments = get_related_names_for_user(db, user.user_id, get_departments_for_user)

    _admin_label = f"{admin.first_name or ''} {admin.last_name or ''}".strip() or admin.email
    create_audit_log(
        db, "User", user.user_id, "create",
        modified_by=admin.user_id,
        modified_by_name=_admin_label,
        new_values={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "login": user.login,
            "roles": roles,
            "departments": departments,
        },
    )

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
    current_user = Depends(get_current_user),
) -> UserNameResponse:
    _ = current_user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist.")
    return UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name)

# NOTE: Double user usage?
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
    _: User = Depends(require_role(["admin", "rapla_editor", "wykladowca_rapla_editor"])),
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
            titles=get_related_names_for_user(db, user.user_id, list_titles_for_user),
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

    _old_values = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "login": user.login,
        "roles": get_related_names_for_user(db, user_id, get_roles_for_user),
        "departments": get_related_names_for_user(db, user_id, get_departments_for_user),
    }

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

    _new_roles = get_related_names_for_user(db, updated.user_id, get_roles_for_user)
    _new_departments = get_related_names_for_user(db, updated.user_id, get_departments_for_user)
    _admin_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "User", user_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=_admin_label,
        old_values=_old_values,
        new_values={
            "first_name": updated.first_name,
            "last_name": updated.last_name,
            "email": updated.email,
            "login": updated.login,
            "roles": _new_roles,
            "departments": _new_departments,
        },
    )

    return AdminUserListResponse(
        user_id=updated.user_id,
        first_name=updated.first_name,
        last_name=updated.last_name,
        album_number=updated.album_number,
        login=updated.login,
        email=updated.email,
        titles=get_related_names_for_user(db, updated.user_id, list_titles_for_user),
        roles=_new_roles,
        departments=_new_departments,
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

    _old_roles = get_related_names_for_user(db, user.user_id, get_roles_for_user)
    _old_values = {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "roles": _old_roles}
    try:
        delete_user_by_admin(db, user)
    except ValueError as exc:
        raise HTTPException(status_code=_status_for_user_validation_error(str(exc)), detail=str(exc)) from exc

    _admin_label = f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email
    create_audit_log(
        db, "User", user_id, "delete",
        modified_by=current_user.user_id,
        modified_by_name=_admin_label,
        old_values=_old_values,
    )


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
    
    # NOTE: Shouldn't here be maybe a check to not reset yours own password?

    set_user_password(db, user, payload.password)
    return ChangePasswordResponse(message="Password reset successfully")


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Pobierz profil zalogowanego użytkownika",
)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    role_names = get_user_role_names(current_user)
    group_code = current_user.student_profile.group.code if current_user.student_profile and current_user.student_profile.group else None

    if "student" in role_names:
        status = "Aktywny student"
    elif role_names.intersection({"wykladowca", "lecturer"}):
        status = "Pracownik dydaktyczny"
    elif role_names.intersection({"planista", "planner"}):
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
        study_track="Ogolnoakademicki" if "student" in role_names else "Nie dotyczy",
        study_mode="Stacjonarne" if "student" in role_names else "Nie dotyczy",
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


@router.put(
    "/me/avatar",
    response_model=AvatarResponse,
    summary="Aktualizuj zdjęcie profilowe zalogowanego użytkownika",
)
def update_my_avatar(
    payload: AvatarUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarResponse:
    if payload.avatar:
        if not (payload.avatar.startswith("data:image/jpeg;base64,") or 
                payload.avatar.startswith("data:image/png;base64,") or
                payload.avatar.startswith("data:image/jpg;base64,")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Niedozwolony format pliku. Dozwolone są tylko JPG i PNG.")
        
        # 10 MB limit w base64 to około 14 MB znaków (10 * 1024 * 1024 * 1.33)
        if len(payload.avatar) > 14 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rozmiar pliku przekracza dozwolone 10 MB.")

    current_user.avatar = payload.avatar
    db.commit()
    db.refresh(current_user)
    return AvatarResponse(avatar=current_user.avatar)


@router.get(
    "/{user_id}/avatar",
    response_model=AvatarResponse,
    summary="Pobierz zdjęcie profilowe użytkownika",
)
def get_user_avatar(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Użytkownik nie istnieje")
    return AvatarResponse(avatar=user.avatar)

