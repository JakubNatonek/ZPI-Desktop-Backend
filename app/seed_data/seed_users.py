import json
import random
import unicodedata
from typing import Optional, cast

from sqlalchemy.orm import Session

from app.cruds.crud_user import get_or_create_user, get_user_by_login
from app.auth.password_utils import hash_password

# role/department/title helpers
from app.models.model_role import Role
from app.models.model_department import Department
from app.cruds.crud_roles_for_user import add_role_to_user
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_title import get_title_by_name, create_title
from app.cruds.crud_title_for_user import add_title_to_user
from app.seed_data.seed_titles import TytulEnum


def _strip_diacritics(s: str) -> str:
    # Normalize and strip diacritics, keep letters only
    nk = unicodedata.normalize("NFKD", s)
    only_ascii = "".join(c for c in nk if not unicodedata.combining(c))
    # Remove non-ASCII letters/digits and spaces
    cleaned = "".join(ch for ch in only_ascii if ch.isalpha())
    return cleaned


def _make_login(first: str, last: str, db: Session, max_attempts: int = 20) -> Optional[str]:
    f = _strip_diacritics(first).lower()
    l = _strip_diacritics(last).lower()

    # Ensure at least 3 chars, pad with 'x' if necessary
    f3 = (f + "xxx")[:3]
    l3 = (l + "xxx")[:3]

    for _ in range(max_attempts):
        digits = "".join(random.choices("0123456789", k=5))
        login = f3 + digits + l3
        if get_user_by_login(db, login) is None:
            return login

    return None


def seed_users(db: Session, path: str = "data/JSON DATA/nauczyciele.json") -> None:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    default_password = "qwerty12345!"
    pw_hash = hash_password(default_password)

    for entry in data:
        last = entry.get("nazwisko") or ""
        first = entry.get("imie") or ""
        t_code = entry.get("tytul")

        if not first or not last:
            continue

        login = _make_login(first, last, db)
        if login is None:
            print(f"Could not generate unique login for {first} {last}; skipping")
            continue

        email = f"{login}@ans-ns.edu.pl"

        # Create or get existing user by email
        try:
            user = get_or_create_user(
                db,
                first_name=first,
                last_name=last,
                login=login,
                email=email,
                password_hash=pw_hash,
                plain_password=None,
                must_change_password=True,
            )
            # assign role 'wykladowca'
            role = db.query(Role).filter(Role.name == "wykladowca").first()
            if role is not None:
                try:
                    add_role_to_user(db, cast(int, user.user_id), cast(int, role.id))
                except Exception:
                    pass

            # assign department NAUK_INZYNIERYJNYCH (abbreviation 'WI')
            dept = db.query(Department).filter(Department.abbreviation == "WI").first()
            if dept is not None:
                try:
                    add_department_to_user(db, cast(int, user.user_id), cast(int, dept.id))
                except Exception:
                    pass

            # attach title if present
            if t_code:
                try:
                    title_value = TytulEnum[t_code].value
                except Exception:
                    title_value = None

                if title_value:
                    title_row = get_title_by_name(db, title_value)
                    if title_row is None:
                        title_row = create_title(db, title_value)

                    try:
                        add_title_to_user(db, cast(int, user.user_id), cast(int, title_row.id))
                    except Exception:
                        pass
            print(f"User created/exists: {login} -> {email}")
        except Exception as e:
            print(f"Error creating user {first} {last}: {e}")

    print("Users seeded.")
