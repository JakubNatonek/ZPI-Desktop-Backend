from typing import Optional
from sqlalchemy.orm import Session

from app.auth.password_utils import apply_password_to_user, verify_password
from app.cruds.crud_user import get_user_by_login
from app.models.model_user import User
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
    apply_password_to_user(user, new_password, must_change_password=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
