import random
import string

from typing import Optional

from sqlalchemy.orm import Session


from app.auth.password_utils import hash_password, verify_password
from app.core.text_normalization import normalize_lookup_value
from app.models.model_user import User, Role, Department


def _find_role_by_name(db: Session, role_name: str) -> Optional[Role]:
    requested_name = normalize_lookup_value(role_name)
    if not requested_name:
        return None

    for role in db.query(Role).all():
        if normalize_lookup_value(role.name) == requested_name:
            return role
    return None


def _find_department_by_name(db: Session, department_name: str) -> Optional[Department]:
    requested_name = normalize_lookup_value(department_name)
    if not requested_name:
        return None

    for department in db.query(Department).all():
        if normalize_lookup_value(department.name) == requested_name:
            return department
    return None



def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """
    Pobierz użytkownika na podstawie loginu.
    """
    return db.query(User).filter(User.login == login).first()



def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Pobierz użytkownika na podstawie adresu e-mail.
    """
    return db.query(User).filter(User.email == email).first()



def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Pobierz użytkownika na podstawie ID.
    """
    return db.query(User).filter(User.user_id == user_id).first()



def _generate_login(db: Session, first_name: str, last_name: str) -> str:
    """
    Generate a unique login: first letter of first name + '.' + last name + 4 digits.
    """
    base = first_name[0].lower() + "." + last_name.lower()
    for _ in range(100):
        suffix = str(random.randint(1000, 9999))
        login = base + suffix
        if get_user_by_login(db, login) is None:
            return login
    raise RuntimeError("Could not generate a unique login after 100 attempts.")



def _generate_password(length: int = 6) -> str:
    """
    Wygeneruj jednorazowe hasło o zadanej długości (litery + cyfry).
    """
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))




def create_user_by_admin(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    role_name: str,
    department_name: str,
) -> User:
    """
    Create a user with auto-generated login and one-time password.
    role_name and department_name are strings matching names in the tables.
    """
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    role_name = role_name.strip()
    department_name = department_name.strip()

    if not first_name:
        raise ValueError("First name cannot be empty")
    if not last_name:
        raise ValueError("Last name cannot be empty")
    if not email:
        raise ValueError("Email cannot be empty")

    login = _generate_login(db, first_name, last_name)
    plain_password = _generate_password()
    hashed = hash_password(plain_password)

    role = _find_role_by_name(db, role_name)
    department = _find_department_by_name(db, department_name)
    if not role:
        raise ValueError(f"Role not found: {role_name}")
    if not department:
        raise ValueError(f"Department not found: {department_name}")

    user = User(
        first_name=first_name,
        last_name=last_name,
        login=login,
        email=email,
        password_hash=hashed,
        plain_password=plain_password,
        must_change_password=True,
        role_id=role.id,
        department_id=department.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def authenticate_user(db: Session, login: str, password: str) -> Optional[User]:
    """
    Sprawdź dane logowania użytkownika i zwróć użytkownika, jeśli są poprawne.
    """
    user = get_user_by_login(db, login)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user



def update_user_password(db: Session, user: User, new_password: str) -> User:
    """
    Zmień hasło użytkownika i wyczyść flagi pierwszego logowania.
    """
    user.password_hash = hash_password(new_password)
    user.plain_password = None
    user.must_change_password = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session) -> list[User]:
    """Get all users sorted by last name and first name."""
    return db.query(User).order_by(User.last_name.asc(), User.first_name.asc()).all()
