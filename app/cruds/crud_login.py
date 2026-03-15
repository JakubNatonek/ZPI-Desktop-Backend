import random
import string

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


def _generate_login(db: Session, imie: str, nazwisko: str) -> str:
    """Generate a unique login: first letter of imie + '.' + nazwisko + 4 random digits."""
    base = imie[0].lower() + "." + nazwisko.lower()
    for _ in range(100):  # guard against infinite loop
        suffix = str(random.randint(1000, 9999))
        login = base + suffix
        if get_user_by_login(db, login) is None:
            return login
    raise RuntimeError("Could not generate a unique login after 100 attempts")


def _generate_password(length: int = 6) -> str:
    """Generate a random one-time password of given length (letters + digits)."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def create_user_by_admin(
    db: Session,
    imie: str,
    nazwisko: str,
    email: str,
    rola: RolaEnum,
    dzial: DzialEnum,
) -> User:
    """Create user with auto-generated login and one-time password."""
    login = _generate_login(db, imie, nazwisko)
    plain_password = _generate_password()
    hashed = hash_password(plain_password)

    user = User(
        imie=imie,
        nazwisko=nazwisko,
        login=login,
        email=email,
        password_hash=hashed,
        plain_password=plain_password,
        must_change_password=True,
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


def update_user_password(db: Session, user: User, new_password: str) -> User:
    """Update password and clear first-login flags after successful change."""
    user.password_hash = hash_password(new_password)
    user.plain_password = None
    user.must_change_password = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
