from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyCookie
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.auth.jwt_utils import decode_access_token
from app.cruds.crud_login import get_user_by_id
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.core.database import get_db
from app.models.model_user import User


access_token_cookie = APIKeyCookie(
    name="access_token",
    scheme_name="AccessTokenCookie",
    description="HttpOnly cookie with access token.",
    auto_error=False,
)


def get_user_role_names(user: User) -> set[str]:
    cached_role_names = getattr(user, "role_names", None)
    if cached_role_names is not None:
        if isinstance(cached_role_names, str):
            cached_iterable = [cached_role_names]
        else:
            cached_iterable = cached_role_names

        return {
            str(role_name).strip().lower()
            for role_name in cached_iterable
            if str(role_name).strip()
        }

    return {
        role_for_user.role.name.strip().lower()
        for role_for_user in getattr(user, "roles_for_user", [])
        if role_for_user.role and role_for_user.role.name and role_for_user.role.name.strip()
    }


def user_has_role(user: User, required_role: str | list[str] | set[str] | tuple[str, ...]) -> bool:
    if isinstance(required_role, str):
        required_role_names = {required_role.strip().lower()} if required_role and required_role.strip() else set()
    else:
        required_role_names = {
            str(role).strip().lower()
            for role in required_role
            if str(role).strip()
        }

    if not required_role_names:
        return False

    user_role_names = get_user_role_names(user)
    return not user_role_names.isdisjoint(required_role_names)


def get_current_user(
    request: Request,
    access_token: str | None = Security(access_token_cookie),
    db: Session = Depends(get_db),
) -> User:
    # Try Bearer header first, then cookie
    token = None
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    if not token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token",
        )

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=401,
            detail="Access token expired",
        ) from exc
    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
        ) from exc

    user_id = payload.get("user_id")
    token_roles_raw = payload.get("roles")
    if user_id is None or not isinstance(token_roles_raw, list) or not token_roles_raw:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token payload",
        )

    token_roles = [str(role).strip().lower() for role in token_roles_raw if str(role).strip()]
    if not token_roles:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token payload",
        )

    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    user_roles = get_roles_for_user(db, user.user_id)
    user_role_values = {
        user_role.name.strip().lower()
        for user_role in user_roles
        if user_role.name and user_role.name.strip()
    }
    if not set(token_roles).intersection(user_role_values):
        raise HTTPException(
            status_code=401,
            detail="Token role mismatch",
        )

    # Cache normalized role names to keep authorization checks consistent.
    setattr(user, "role_names", list(user_role_values))

    return user
