import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.auth.jwt_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    refresh_expiry_datetime,
)
from app.cruds.crud_departments_for_user import get_departments_for_user
from app.cruds.crud_login import (
    authenticate_user,
    get_user_by_id,
    update_user_password,
)
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_refresh_token import (
    create_refresh_session,
    is_refresh_session_active,
    revoke_refresh_session,
)
from app.core.database import get_db
from app.models.model_user import User
from app.schemas.user import (
    AuthResponse,
    AuthMeResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    CurrentUserResponse,
    UserNameResponse,
    UserLogin,
)

router = APIRouter(prefix="/auth", tags=["auth"])

load_dotenv()

REFRESH_COOKIE_NAME = os.getenv("REFRESH_COOKIE_NAME", "refresh_token")
REFRESH_COOKIE_SECURE = os.getenv("REFRESH_COOKIE_SECURE", "false").lower() == "true"
REFRESH_COOKIE_SAMESITE = os.getenv("REFRESH_COOKIE_SAMESITE", "lax")


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=REFRESH_COOKIE_SECURE,
        samesite=REFRESH_COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


def _resolve_primary_role(role_names: list[str]) -> str:
    normalized_roles = [role.strip().lower() for role in role_names if role and role.strip()]

    for candidate in ("admin", "wykladowca", "lecturer", "planista", "planner", "student"):
        if candidate in normalized_roles:
            return candidate

    return normalized_roles[0] if normalized_roles else "admin"


@router.get(
    "/me",
    response_model=AuthMeResponse,
    summary="Dane zalogowanego użytkownika dla warstwy auth",
)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthMeResponse:
    role_names = [role.name.strip().lower() for role in get_roles_for_user(db, current_user.user_id) if role.name]
    department_names = [department.name.strip() for department in get_departments_for_user(db, current_user.user_id) if department.name]

    return AuthMeResponse(
        user_id=current_user.user_id,
        login=current_user.login,
        email=current_user.email,
        role=_resolve_primary_role(role_names),
        department=department_names[0] if department_names else "",
    )


@router.post(
    "/",
    response_model=AuthResponse,
    summary="Zaloguj użytkownika",
)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload.login, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    if getattr(user, "is_blocked", False):
        raise HTTPException(status_code=403, detail="Twoje konto zostało zablokowane. Skontaktuj się z administratorem.")

    role_names = [role.name.strip().lower() for role in get_roles_for_user(db, user.user_id) if role.name]
    access_token = create_access_token(user_id=user.user_id, roles=role_names)
    refresh_token, refresh_jti = create_refresh_token(user_id=user.user_id, roles=role_names)
    create_refresh_session(
        db,
        user_id=user.user_id,
        jti=refresh_jti,
        expires_at=refresh_expiry_datetime(),
    )
    _set_refresh_cookie(response, refresh_token)
    # Ustaw access_token jako cookie httponly
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=REFRESH_COOKIE_SECURE,
        samesite=REFRESH_COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return AuthResponse(
        user_id=user.user_id,
        login=user.login,
        email=user.email,
        access_token=access_token,
        access_token_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Odśwież tokeny",
)
def refresh_tokens(request: Request, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token cookie")

    try:
        token_payload = decode_refresh_token(refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token") from exc

    user_id = token_payload.get("user_id")
    refresh_jti = token_payload.get("jti")
    if user_id is None or refresh_jti is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    if not is_refresh_session_active(db, str(refresh_jti)):
        raise HTTPException(status_code=401, detail="Refresh token revoked or unknown")

    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    role_names = [role.name.strip().lower() for role in get_roles_for_user(db, user.user_id) if role.name]
    access_token = create_access_token(user_id=user.user_id, roles=role_names)
    new_refresh_token, new_refresh_jti = create_refresh_token(user_id=user.user_id, roles=role_names)

    revoke_refresh_session(db, str(refresh_jti))
    create_refresh_session(
        db,
        user_id=user.user_id,
        jti=new_refresh_jti,
        expires_at=refresh_expiry_datetime(),
    )

    _set_refresh_cookie(response, new_refresh_token)
    # Ustaw access_token jako cookie httponly
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=REFRESH_COOKIE_SECURE,
        samesite=REFRESH_COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return AuthResponse(
        user_id=user.user_id,
        login=user.login,
        email=user.email,
        access_token=access_token,
        access_token_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        must_change_password=user.must_change_password,
    )


@router.post(
    "/change-one-time-password",
    response_model=ChangePasswordResponse,
    summary="Zmień jednorazowe hasło użytkownika",
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChangePasswordResponse:
    update_user_password(db, current_user, payload.new_password)
    return ChangePasswordResponse(message="One-time password changed successfully")


@router.post(
    "/logout",
    summary="Wyloguj użytkownika",
)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)

    if refresh_token:
        try:
            token_payload = decode_refresh_token(refresh_token)
            refresh_jti = token_payload.get("jti")
            if refresh_jti:
                revoke_refresh_session(db, str(refresh_jti))
        except JWTError:
            # We still clear cookie even if token is malformed/expired.
            pass

        response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
        response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out"}



