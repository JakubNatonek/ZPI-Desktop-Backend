from fastapi import Depends, HTTPException, Request
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.orm import Session

from app.auth.jwt_utils import decode_access_token
from app.cruds.crud_login import get_user_by_id
from app.core.database import get_db
from app.models.model_user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token cookie",
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
    role = payload.get("role")
    if user_id is None or role is None:
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

    user_role_value = user.role.name if user.role else str(user.role)
    if user_role_value != str(role):
        raise HTTPException(
            status_code=401,
            detail="Token role mismatch",
        )

    return user
