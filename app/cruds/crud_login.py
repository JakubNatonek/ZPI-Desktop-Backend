from sqlalchemy.orm import Session
from app.auth.password_utils import hash_password, verify_password
from app.models.model_user import DzialEnum, RolaEnum, User


def get_user_by_login(db: Session, login: str) -> User | None:
    """Fetch user by login."""
    return db.query(User).filter(User.login == login).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch user by id."""
    return db.query(User).filter(User.user_id == user_id).first()


def create_user_by_admin(
    db: Session,
    login: str,
    email: str,
    password_hash: str,
    rola: RolaEnum,
    dzial: DzialEnum,
) -> User:
    """Create user from admin-provided data."""
    stored_password_hash = password_hash
    if not password_hash.startswith("$2"):
        stored_password_hash = hash_password(password_hash)

    user = User(
        login=login,
        email=email,
        password_hash=stored_password_hash,
        rola=rola.value,
        dzial=dzial.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, login: str, password: str) -> User | None:
    """Verify user credentials and return user if valid."""
    user = get_user_by_login(db, login)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
