from typing import Callable, Optional, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table, cast, func, Integer, insert, update
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.auth.password_utils import apply_password_to_user, hash_password
from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_refresh_token import RefreshTokenSession
from app.models.model_role import Role
from app.models.model_role_for_user import RolesForUser
from app.models.model_title import TitleModel
from app.models.model_title_for_user import TitleForUser
from app.models.model_user import User
from app.models.rapla.model_rapla_app_user_to_resourc import RaplaAppUserToResourc
from app.models.rapla.model_rapla_user_to_app_user import RaplaUserToAppUser

RelatedItem = TypeVar("RelatedItem")

def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.last_name.asc(), User.first_name.asc()).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter(User.login == login).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_album_number(db: Session, album_number: str) -> Optional[User]:
    return db.query(User).filter(User.album_number == album_number).first()


def create_user(
    db: Session,
    first_name: str,
    last_name: str,
    login: str,
    email: str,
    password_hash: str,

    album_number: str | None = None,
    public_key: str | None = None,
    must_change_password: bool | None = None,
    last_seen_at: datetime | None = None,
) -> User:
    # Check login uniqueness
    login_exists = (
        db.query(User)
        .filter(User.login == login)
        .first()
    )
    if login_exists:
        raise ValueError(f"Login already exists: {login}")

    # Check email uniqueness
    email_exists = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
    if email_exists:
        raise ValueError(f"Email already exists: {email}")

    # If album_number not provided, generate next numeric album number (zero-padded 5 digits)
    if album_number is None:
        max_album_number = db.query(func.max(cast(User.album_number, Integer))).scalar()
        next_number = int(max_album_number or 0) + 1
        album_number = f"{next_number:05d}"

    # Check album_number uniqueness
    album_exists = db.query(User).filter(User.album_number == album_number).first()
    if album_exists:
        raise ValueError(f"Album number already exists: {album_number}")

    user = User(
        first_name = first_name,
        last_name = last_name,
        album_number = album_number,
        login = login,
        email = email,
        public_key = public_key,
        password_hash = password_hash,
        must_change_password = must_change_password,
        last_seen_at = last_seen_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _generate_album_number(db: Session) -> str:
    max_album_number = db.query(func.max(cast(User.album_number, Integer))).scalar()
    next_number = int(max_album_number or 0) + 1
    return f"{next_number:05d}"


def _generate_login(first_name: str, last_name: str, album_number: str) -> str:
    return first_name[0].lower() + last_name[0].lower() + album_number


def _get_users_table(db: Session) -> Table:
    metadata = MetaData()
    return Table("users", metadata, autoload_with=db.get_bind())


def _legacy_user_fk_values(users_table: Table, role_id: int, department_id: int) -> dict[str, int]:
    values: dict[str, int] = {}
    if "role_id" in users_table.c:
        values["role_id"] = role_id
    if "department_id" in users_table.c:
        values["department_id"] = department_id
    return values


def _map_user_integrity_error(exc: IntegrityError) -> ValueError:
    error_text = str(getattr(exc, "orig", exc)).lower()

    if 'null value in column "department_id"' in error_text:
        return ValueError("Primary department is required by current database schema")
    if 'null value in column "role_id"' in error_text:
        return ValueError("Primary role is required by current database schema")
    if "foreign key" in error_text and "department_id" in error_text:
        return ValueError("Selected primary department does not exist")
    if "foreign key" in error_text and "role_id" in error_text:
        return ValueError("Selected primary role does not exist")

    if "users_login_key" in error_text or "login" in error_text:
        return ValueError("User with this login already exists")
    if "users_email_key" in error_text or "email" in error_text:
        return ValueError("User with this email already exists")
    if "users_album_number_key" in error_text or "album_number" in error_text:
        return ValueError("User with this album number already exists")

    return ValueError("Database constraint error while saving user")


def create_user_by_admin(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    role_ids: list[int],
    department_ids: list[int],
    password: str,
    title_ids: list[int] | None = None,
) -> User:
    album_number = _generate_album_number(db)
    login = _generate_login(first_name, last_name, album_number)

    if get_user_by_login(db, login) is not None:
        raise ValueError(f"Generated login already exists: {login}")
    if get_user_by_album_number(db, album_number) is not None:
        raise ValueError(f"Generated album number already exists: {album_number}")

    if not role_ids:
        raise ValueError("At least one role must be provided")
    if not department_ids:
        raise ValueError("At least one department must be provided")

    roles: list[Role] = []
    for role_id in dict.fromkeys(role_ids):
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        roles.append(role)

    departments: list[Department] = []
    for department_id in dict.fromkeys(department_ids):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise ValueError(f"Department not found: {department_id}")
        departments.append(department)

    titles: list[TitleModel] = []
    for title_id in dict.fromkeys(title_ids or []):
        title = db.query(TitleModel).filter(TitleModel.id == title_id).first()
        if not title:
            raise ValueError(f"Title not found: {title_id}")
        titles.append(title)

    users_table = _get_users_table(db)
    insert_values = {
        "first_name": first_name,
        "last_name": last_name,
        "album_number": album_number,
        "login": login,
        "email": email,
        "password_hash": hash_password(password),
        "must_change_password": True,
    }
    insert_values.update(_legacy_user_fk_values(users_table, roles[0].id, departments[0].id))

    try:
        insert_stmt = insert(users_table).values(**insert_values).returning(users_table.c.user_id)
        user_id = int(db.execute(insert_stmt).scalar_one())

        for role in roles:
            db.add(RolesForUser(user_id=user_id, role_id=role.id))
        for department in departments:
            db.add(DepartmentsForUser(user_id=user_id, department_id=department.id))
        for title in titles:
            db.add(TitleForUser(user_id=user_id, title_id=title.id))

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _map_user_integrity_error(exc) from exc

    user = get_user_by_id(db, user_id)
    if user is None:
        raise ValueError("User was created but could not be loaded")
    return user


def update_user_by_admin(
    db: Session,
    user: User,
    first_name: str,
    last_name: str,
    login: str,
    email: str,
    role_ids: list[int],
    department_ids: list[int],
) -> User:
    user.first_name = first_name
    user.last_name = last_name
    user.login = login
    user.email = email

    if not role_ids:
        raise ValueError("At least one role must be provided")
    if not department_ids:
        raise ValueError("At least one department must be provided")

    roles: list[Role] = []
    for role_id in dict.fromkeys(role_ids):
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        roles.append(role)

    departments: list[Department] = []
    for department_id in dict.fromkeys(department_ids):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise ValueError(f"Department not found: {department_id}")
        departments.append(department)

    db.add(user)
    db.query(RolesForUser).filter(RolesForUser.user_id == user.user_id).delete(synchronize_session=False)
    db.query(DepartmentsForUser).filter(DepartmentsForUser.user_id == user.user_id).delete(synchronize_session=False)
    for role in roles:
        db.add(RolesForUser(user_id=user.user_id, role_id=role.id))
    for department in departments:
        db.add(DepartmentsForUser(user_id=user.user_id, department_id=department.id))

    users_table = _get_users_table(db)
    legacy_fk_values = _legacy_user_fk_values(users_table, roles[0].id, departments[0].id)

    try:
        if legacy_fk_values:
            db.execute(
                update(users_table)
                .where(users_table.c.user_id == user.user_id)
                .values(**legacy_fk_values)
            )

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _map_user_integrity_error(exc) from exc

    db.refresh(user)
    return user


def delete_user_by_admin(db: Session, user: User) -> None:
    db.query(RolesForUser).filter(RolesForUser.user_id == user.user_id).delete(synchronize_session=False)
    db.query(DepartmentsForUser).filter(DepartmentsForUser.user_id == user.user_id).delete(synchronize_session=False)
    db.query(TitleForUser).filter(TitleForUser.user_id == user.user_id).delete(synchronize_session=False)
    db.query(RefreshTokenSession).filter(RefreshTokenSession.user_id == user.user_id).delete(synchronize_session=False)
    db.query(RaplaAppUserToResourc).filter(RaplaAppUserToResourc.app_user_id == user.user_id).delete(synchronize_session=False)
    db.query(RaplaUserToAppUser).filter(RaplaUserToAppUser.app_user_id == user.user_id).delete(synchronize_session=False)
    db.delete(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("User cannot be deleted because related records still exist") from exc


def set_user_password(db: Session, user: User, password: str) -> User:
    apply_password_to_user(user, password, must_change_password=True)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    album_number: str | None = None,
    login: str | None = None,
    email: str | None = None,
    public_key: str | None = None,
    password_hash: str | None = None,
    must_change_password: bool | None = None,
    last_seen_at: datetime | None = None,
) -> User | None:
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    if first_name is not None:
        user.first_name = first_name  # type: ignore
    if last_name is not None:
        user.last_name = last_name  # type: ignore
    if login is not None and login != user.login:
        conflict = (
            db.query(User)
            .filter(User.login == login, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Login already exists: {login}")
        user.login = login  # type: ignore
    if email is not None and email != user.email:
        conflict = (
            db.query(User)
            .filter(User.email == email, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Email already exists: {email}")
        user.email = email  # type: ignore
    if album_number is not None and album_number != user.album_number:
        conflict = (
            db.query(User)
            .filter(User.album_number == album_number, User.user_id != user_id)
            .first()
        )
        if conflict:
            raise ValueError(f"Album number already exists: {album_number}")
        user.album_number = album_number  # type: ignore
    if public_key is not None:
        user.public_key = public_key  # type: ignore
    if last_seen_at is not None:
        user.last_seen_at = last_seen_at  # type: ignore
    if password_hash is not None:
        user.password_hash = password_hash  # type: ignore
    if must_change_password is not None:
        user.must_change_password = must_change_password  # type: ignore

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True


def get_related_names_for_user(
    db: Session,
    user_id: int,
    fetch_related: Callable[[Session, int], list[RelatedItem]],
) -> list[str]:
    related_items = fetch_related(db, user_id)
    return [str(getattr(item, "name", "")).strip() for item in related_items if getattr(item, "name", None)]

