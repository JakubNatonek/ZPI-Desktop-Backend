from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], argon2__type="ID", deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
