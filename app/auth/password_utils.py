from passlib.context import CryptContext

from app.models.model_user import User

pwd_context = CryptContext(schemes=["argon2"], default="argon2", deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using Argon2."""
    return pwd_context.hash(password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(raw_password, hashed_password)


def apply_password_to_user(user: User, password: str, *, must_change_password: bool | None = None) -> User:
    """Hash a password and assign it to a user object."""
    user.password_hash = hash_password(password)
    if must_change_password is not None:
        user.must_change_password = must_change_password
    return user
