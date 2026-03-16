
import random
import string
from typing import Optional

from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password, verify_password
from app.models.model_user import DzialEnum, RolaEnum, User



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



def _generate_login(db: Session, imie: str, nazwisko: str) -> str:
    """
    Wygeneruj unikalny login: pierwsza litera imienia + '.' + nazwisko + 4 cyfry.
    """
    base = imie[0].lower() + "." + nazwisko.lower()
    for _ in range(100):
        suffix = str(random.randint(1000, 9999))
        login = base + suffix
        if get_user_by_login(db, login) is None:
            return login
    raise RuntimeError("Nie udało się wygenerować unikalnego loginu po 100 próbach.")



def _generate_password(length: int = 6) -> str:
    """
    Wygeneruj jednorazowe hasło o zadanej długości (litery + cyfry).
    """
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
    """
    Utwórz użytkownika z automatycznie generowanym loginem i jednorazowym hasłem.
    """
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
