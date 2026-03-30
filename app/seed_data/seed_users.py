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
from app.cruds.crud_roles_for_user import get_roles_for_user

# rapla helpers
from app.models.rapla.model_rapla_user import RaplaUser as RaplaUserModel
from app.models.rapla.model_rapla_resourc import ModelRaplaResourc
from app.models.model_user import User
from app.cruds.rapla.crud_rapla_resourc import create_resourc
from app.cruds.rapla.crud_rapla_app_user_to_resourc import create_app_user_to_resourc_mapping
from app.cruds.rapla.crud_rapla_permission import get_permission_by_access, create_permission
from app.cruds.rapla.crud_rapla_permission_for_resourc import create_permission_for_resourc


def _assign_role_to_user(db: Session, user: User):
    # assign role 'wykladowca'
    role = db.query(Role).filter(Role.name == "wykladowca").first()
    if role is not None:
        try:
            add_role_to_user(db, cast(int, user.user_id), cast(int, role.id))
            print(f"Assigned role 'wykladowca' to {user.login}")
        except Exception:
            print(f"Role 'wykladowca' already assigned to {user.login} or assignment failed")



def _assign_title_to_user(db: Session, user: User, t_code: str | None):
    if not t_code:
        return
    try:
        title_value = TytulEnum[t_code].value
    except Exception:
        return

    if not title_value:
        return

    title_row = get_title_by_name(db, title_value)
    if title_row is None:
        title_row = create_title(db, title_value)

    try:
        add_title_to_user(db, cast(int, user.user_id), cast(int, title_row.id))
    except Exception:
        pass


def _assign_department_to_user(db: Session, user: User):
    dept = db.query(Department).filter(Department.abbreviation == "WI").first()
    if dept is None:
        return
    try:
        add_department_to_user(db, cast(int, user.user_id), cast(int, dept.id))
    except Exception:
        pass


def _ensure_rapla_resource_for_user(db: Session, user: User, login: str):
    roles = get_roles_for_user(db, cast(int, user.user_id))
    if not any(r.name == "wykladowca" for r in roles):
        return None

    rapla_admin = db.query(RaplaUserModel).filter(RaplaUserModel.username == "admin").first()
    if rapla_admin is None:
        print(f"Rapla admin user not found; skipping Rapla resource creation for {login}")
        return None

    owner_uuid = cast(str, rapla_admin.uuid)
    try:
        res = create_resourc(db, owner=owner_uuid)
        print(f"Created Rapla resource id={res.id} uuid={res.uuid} for app user {login}")
    except Exception as e:
        print(f"Failed to create Rapla resource for {login}: {e}")
        return None

    try:
        create_app_user_to_resourc_mapping(db, cast(int, user.user_id), cast(int, res.id))
        print(f"Mapped app user {login} -> rapla_resourc id={res.id}")
    except Exception as e:
        print(f"Failed to map app user {login} to rapla resource id={getattr(res, 'id', None)}: {e}")

    return res


def _ensure_permission_for_resource(db: Session, res: ModelRaplaResourc):
    if res is None:
        return None
    perm = get_permission_by_access(db, access="allocate_conflicts")
    if perm is None:
        perm = create_permission(db, access="allocate_conflicts")
    try:
        create_permission_for_resourc(db, cast(int, res.id), cast(int, perm.id))
        print(f"Assigned permission allocate_conflicts to rapla_resourc id={res.id}")
    except Exception as e:
        print(f"Failed to assign permission to rapla_resourc id={res.id}: {e}")
    return perm


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
        t_code = entry.get("tytul") or None

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
            _assign_role_to_user(db, user)
            _assign_title_to_user(db, user, t_code)
            _assign_department_to_user(db, user)

            # create rapla resource, mapping and permission if user is a lecturer
            res = _ensure_rapla_resource_for_user(db, user, login)
            _ensure_permission_for_resource(db, res)

            print(f"User created/exists: {login} -> {email}")
        except Exception as e:
            print(f"Error creating user {first} {last}: {e}")

    print("Users seeded.")
