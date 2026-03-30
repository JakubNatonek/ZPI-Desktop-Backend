from typing import Optional
from sqlalchemy.orm import Session

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
    plain_password: Optional[str] = None,
    must_change_password: bool = False,
) -> User:
    # Check login uniqueness
    login_exists = db.query(User).filter(User.login == login).first()
    if login_exists:
        raise ValueError(f"Login already exists: {login}")

    # Check email uniqueness
    email_exists = db.query(User).filter(User.email == email).first()
    if email_exists:
        raise ValueError(f"Email already exists: {email}")

    user = User(
        first_name=first_name,
        last_name=last_name,
        login=login,
        email=email,
        password_hash=password_hash,
        plain_password=plain_password,
        must_change_password=must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(
    db: Session,
    first_name: str,
    last_name: str,
    login: str,
    email: str,
    password_hash: str,
    plain_password: Optional[str] = None,
    must_change_password: bool = False,
) -> User:
    existing = get_user_by_email(db, email)
    if existing:
        return existing

    return create_user(
        db=db,
        first_name=first_name,
        last_name=last_name,
        login=login,
        email=email,
        password_hash=password_hash,
        plain_password=plain_password,
        must_change_password=must_change_password,
    )


def update_user(
    db: Session,
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    login: Optional[str] = None,
    email: Optional[str] = None,
    password_hash: Optional[str] = None,
    plain_password: Optional[str] = None,
    must_change_password: Optional[bool] = None,
) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    if first_name is not None:
        user.first_name = first_name  # type: ignore
    if last_name is not None:
        user.last_name = last_name  # type: ignore
    if login is not None and login != user.login:
        conflict = db.query(User).filter(User.login == login, User.user_id != user_id).first()
        if conflict:
            raise ValueError(f"Login already exists: {login}")
        user.login = login  # type: ignore
    if email is not None and email != user.email:
        conflict = db.query(User).filter(User.email == email, User.user_id != user_id).first()
        if conflict:
            raise ValueError(f"Email already exists: {email}")
        user.email = email  # type: ignore
    if password_hash is not None:
        user.password_hash = password_hash  # type: ignore
    if plain_password is not None:
        user.plain_password = plain_password  # type: ignore
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

