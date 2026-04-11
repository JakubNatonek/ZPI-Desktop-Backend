from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import cast, func, Integer
from datetime import datetime

from app.models.model_user import User

def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.user_id.asc()).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter(User.login == login).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    first_name: str,
    last_name: str,
    login: str,
    email: str,
    password_hash: str,

    album_number: str | None = None,
    public_key: str | None = None,
    must_change_password: bool | None = None,
    last_seen_at: datetime | None = None,
) -> User:
    # Check login uniqueness
    login_exists = (
        db.query(User)
        .filter(User.login == login)
        .first()
    )
    if login_exists:
        raise ValueError(f"Login already exists: {login}")

    # Check email uniqueness
    email_exists = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    if email_exists:
        raise ValueError(f"Email already exists: {email}")

    # If album_number not provided, generate next numeric album number (zero-padded 5 digits)
    if album_number is None:
        max_album_number = db.query(func.max(cast(User.album_number, Integer))).scalar()
        next_number = int(max_album_number or 0) + 1
        album_number = f"{next_number:05d}"

    # Check album_number uniqueness
    album_exists = db.query(User).filter(User.album_number == album_number).first()
    if album_exists:
        raise ValueError(f"Album number already exists: {album_number}")

    user = User(
        first_name = first_name,
        last_name = last_name,
        album_number = album_number,
        login = login,
        email = email,
        public_key = public_key,
        password_hash = password_hash,
        must_change_password = must_change_password,
        last_seen_at = last_seen_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    album_number: str | None = None,
    login: str | None = None,
    email: str | None = None,
    public_key: str | None = None,
    password_hash: str | None = None,
    must_change_password: bool | None = None,
    last_seen_at: datetime | None = None,
) -> User | None:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    if first_name is not None:
        user.first_name = first_name  # type: ignore
    if last_name is not None:
        user.last_name = last_name  # type: ignore
    if login is not None and login != user.login:
        conflict = (
            db.query(User)
            .filter(User.login == login, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Login already exists: {login}")
        user.login = login  # type: ignore
    if email is not None and email != user.email:
        conflict = (
            db.query(User)
            .filter(User.email == email, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Email already exists: {email}")
        user.email = email  # type: ignore
    if album_number is not None and album_number != user.album_number:
        conflict = (
            db.query(User)
            .filter(User.album_number == album_number, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Album number already exists: {album_number}")
        user.album_number = album_number  # type: ignore
    if public_key is not None:
        user.public_key = public_key  # type: ignore
    if last_seen_at is not None:
        user.last_seen_at = last_seen_at  # type: ignore
    if password_hash is not None:
        user.password_hash = password_hash  # type: ignore
    if must_change_password is not None:
        user.must_change_password = must_change_password  # type: ignore

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True

