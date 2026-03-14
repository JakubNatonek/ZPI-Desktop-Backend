import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.auth.jwt_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    refresh_expiry_datetime,
)
from app.cruds.crud_login import (
    authenticate_user,
    create_user_by_admin,
    get_user_by_email,
    get_user_by_id,
    get_user_by_login,
)
from app.cruds.crud_refresh_token import (
    create_refresh_session,
    is_refresh_session_active,
    revoke_refresh_session,
)
from app.database import get_db
from app.models.model_user import User
from app.schemas.user import (
    AuthResponse,
    AdminUserCreate,
    CurrentUserResponse,
    UserLogin,
)


router = APIRouter(prefix="/auth", tags=["auth"])

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
        path="/auth",
    )


@router.post("/create", status_code=201)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db)) -> dict[str, str | int]:
    existing_login = get_user_by_login(db, payload.login)
    if existing_login is not None:
        raise HTTPException(status_code=409, detail="User with this login already exists")

    existing_email = get_user_by_email(db, payload.email)
    if existing_email is not None:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    user = create_user_by_admin(
        db,
        payload.login,
        payload.email,
        payload.password_hash,
        payload.rola,
        payload.dzial,
    )

    return {
        "user_id": user.user_id,
        "login": user.login,
        "email": user.email,
        "message": "User created",
    }


@router.post("/", response_model=AuthResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload.login, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    access_token = create_access_token(user_id=user.user_id, role=user.rola)
    refresh_token, refresh_jti = create_refresh_token(user_id=user.user_id, role=user.rola)
    create_refresh_session(
        db,
        user_id=user.user_id,
        jti=refresh_jti,
        expires_at=refresh_expiry_datetime(),
    )
    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(
        user_id=user.user_id,
        login=user.login,
        email=user.email,
        access_token=access_token,
        access_token_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=AuthResponse)
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

    access_token = create_access_token(user_id=user.user_id, role=user.rola)
    new_refresh_token, new_refresh_jti = create_refresh_token(user_id=user.user_id, role=user.rola)

    revoke_refresh_session(db, str(refresh_jti))
    create_refresh_session(
        db,
        user_id=user.user_id,
        jti=new_refresh_jti,
        expires_at=refresh_expiry_datetime(),
    )

    _set_refresh_cookie(response, new_refresh_token)

    return AuthResponse(
        user_id=user.user_id,
        login=user.login,
        email=user.email,
        access_token=access_token,
        access_token_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
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

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/auth")
    return {"message": "Logged out"}


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(
        user_id=current_user.user_id,
        login=current_user.login,
        email=current_user.email,
        role=current_user.rola,
        dzial=current_user.dzial,
    )
