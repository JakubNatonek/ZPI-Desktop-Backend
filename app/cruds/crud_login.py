import random
import string

from typing import Optional

from sqlalchemy import cast, func, Integer
from sqlalchemy.orm import Session


from app.auth.password_utils import hash_password, verify_password
from app.models.model_user import User
from app.models.model_role import Role
from app.models.model_department import Department
from app.core.text_normalization import normalize_lookup_value

## NOTE/TODO: Chenge to use dedicated cruds
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
## END OF NOTE/TODO


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """
    Pobierz użytkownika na podstawie loginu.
    """
    return db.query(User).filter(User.login == login).first()


def get_user_by_album_number(db: Session, album_number: str) -> Optional[User]:
    """
    Pobierz użytkownika na podstawie numeru albumu.
    """
    return db.query(User).filter(User.album_number == album_number).first()



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


## NOTE/TODO: Chenge seed users to use new login generation
def _generate_album_number(db: Session) -> str:
    """
    Generate the next album number in format 00001, 00002, ...
    """
    max_album_number = db.query(func.max(cast(User.album_number, Integer))).scalar()
    next_number = int(max_album_number or 0) + 1
    return f"{next_number:05d}"


def _generate_login(first_name: str, last_name: str, album_number: str) -> str:
    """
    Generate login as first letter of first name + first letter of last name + album number.
    Example: Jan Kowalski + 00001 -> jk00001
    """
    return first_name[0].lower() + last_name[0].lower() + album_number



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
    role_id: int,
    department_id: int,
    # NOTE: Why is this a string instead of a boolean ? (one_time_password)
    one_time_password: str | None = None, 
) -> User:
    """
    Create a user with auto-generated album number, login and one-time password.
    role_id and department_id must reference existing records.
    """
    album_number = _generate_album_number(db)
    login = _generate_login(first_name, last_name, album_number)

    if get_user_by_login(db, login) is not None:
        raise ValueError(f"Generated login already exists: {login}")
    if get_user_by_album_number(db, album_number) is not None:
        raise ValueError(f"Generated album number already exists: {album_number}")

    plain_password = one_time_password or _generate_password()
    hashed = hash_password(plain_password)

    # NOTE/TODO: Chenge role and department to use dedicated crude. Not a raw query.
    role = db.query(Role).filter(Role.id == role_id).first()
    department = db.query(Department).filter(Department.id == department_id).first()
    if not role:
        raise ValueError(f"Role not found: {role_id}")
    if not department:
        raise ValueError(f"Department not found: {department_id}")

    user = User(
        first_name=first_name,
        last_name=last_name,
        album_number=album_number,
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


def update_user_by_admin(
    db: Session,
    user: User,
    first_name: str,
    last_name: str,
    login: str,
    email: str,
    role: Role,
    department: Department,
) -> User:
    user.first_name = first_name
    user.last_name = last_name
    user.login = login
    user.email = email
    user.role_id = role.id
    user.department_id = department.id

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_admin(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def set_user_one_time_password(db: Session, user: User, one_time_password: str) -> User:
    user.password_hash = hash_password(one_time_password)
    user.plain_password = one_time_password
    user.must_change_password = True

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
