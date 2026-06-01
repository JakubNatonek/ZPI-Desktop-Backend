from fastapi import Depends, HTTPException, Request
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session
import unicodedata

from app.auth.jwt_utils import decode_access_token
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_user import get_user_by_id
from app.core.database import get_db
from app.models.model_user import User


def _normalize_role_name(role_name: str) -> str:
    normalized = str(role_name).strip().lower().replace("ł", "l")
    normalized = unicodedata.normalize("NFKD", normalized)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def get_user_role_names(user: User) -> set[str]:
    return {
        _normalize_role_name(role_for_user.role.name)
        for role_for_user in getattr(user, "roles_for_user", [])
        if role_for_user.role and role_for_user.role.name
    }


def user_has_role(user: User, required_role: str | list[str] | set[str] | tuple[str, ...]) -> bool:
    if isinstance(required_role, str):
        required_role_names = {_normalize_role_name(required_role)} if required_role else set()
    else:
        required_role_names = {
            _normalize_role_name(str(role))
            for role in required_role
            if str(role)
        }

    if not required_role_names:
        return False

    user_role_names = get_user_role_names(user)
    return not user_role_names.isdisjoint(required_role_names)


def _extract_access_token(request: Request) -> str | None:
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "bearer" and credentials.strip():
            return credentials.strip()

    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    access_token = _extract_access_token(request)
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token",
        )

    try:
        payload = decode_access_token(access_token)
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

    token_roles = [_normalize_role_name(str(role)) for role in token_roles_raw if str(role).strip()]
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
    user_role_values = {_normalize_role_name(user_role.name) for user_role in user_roles if user_role.name}
    if not set(token_roles).intersection(user_role_values):
        raise HTTPException(
            status_code=401,
            detail="Token role mismatch",
        )

    return user
