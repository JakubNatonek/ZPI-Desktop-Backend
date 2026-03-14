import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def _create_token(
    user_id: int,
    role: str,
    token_type: str,
    expires_delta: timedelta,
    jti: str | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "user_id": user_id,
        "role": role,
        "type": token_type,
        "exp": expire,
    }
    if jti is not None:
        payload["jti"] = jti
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(user_id: int, role: str) -> str:
    return _create_token(
        user_id=user_id,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int, role: str) -> tuple[str, str]:
    refresh_jti = str(uuid4())
    token = _create_token(
        user_id=user_id,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        jti=refresh_jti,
    )
    return token, refresh_jti


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    return payload


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload


def refresh_expiry_datetime() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)