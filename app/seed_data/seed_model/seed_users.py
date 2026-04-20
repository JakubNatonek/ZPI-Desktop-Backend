import json

from typing import  cast

import json
import random
import unicodedata
from typing import cast, Optional

from sqlalchemy.orm import Session

from app.cruds.crud_user import create_user_by_admin, get_user_by_login
from app.cruds.crud_title import get_title_by_name, create_title
from app.seed_data.seed_model.seed_titles import TytulEnum
from app.cruds.crud_role import get_role_by_name
from app.cruds.crud_department import get_department_by_abbreviation


def _strip_diacritics(s: str) -> str:
    nk = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nk if not unicodedata.combining(c) and c.isalpha())


def _make_login(first: str, last: str, db: Session, max_attempts: int = 20) -> Optional[str]:
    f = _strip_diacritics(first).lower()
    l = _strip_diacritics(last).lower()
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

    default_password = "test123"

    for entry in data:
        last = entry.get("nazwisko") or ""
        first = entry.get("imie") or ""
        t_code = entry.get("tytul") or None

        if not first or not last:
            continue

        # prepare role and department rows
        role = get_role_by_name(db=db, name="wykladowca")
        if role is None:
            print(f"Role 'wykladowca' not found; skipping user {first} {last}")
            continue

        dept = get_department_by_abbreviation(db=db, abbreviation="WI")
        if dept is None:
            print(f"Department 'WI' not found; skipping user {first} {last}")
            continue

        # prepare title id if present
        title_row = None
        if t_code:
            try:
                title_value = TytulEnum[t_code].value
            except Exception:
                title_value = None
            if title_value:
                title_row = get_title_by_name(db, title_value)
                if title_row is None:
                    title_row = create_title(db, title_value)

        title_ids = [cast(int, title_row.id)] if title_row is not None else None

        try:
            user = create_user_by_admin(
                db=db,
                first_name=first,
                last_name=last,
                role_ids=[cast(int, role.id)],
                department_ids=[cast(int, dept.id)],
                password=default_password,
                title_ids=title_ids,
                admin=None,
            )

        except Exception as e:
            print(f"Error creating user {first} {last}: {e}")

    print("Users seeded.")
