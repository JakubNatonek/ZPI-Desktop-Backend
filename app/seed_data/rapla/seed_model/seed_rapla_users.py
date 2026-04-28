from typing import cast

from sqlalchemy.orm import Session

from app.cruds.rapla.crud_rapla_categories import get_rapla_category_by_key
from app.cruds.rapla.crud_rapla_group_for_user import add_rapla_group_for_user
from app.cruds.rapla.crud_rapla_users import create_rapla_user
from app.models.model_department import Department
from app.models.rapla.model_rapla_user import RaplaUser


def _ensure_department_editor_user(db: Session, abbreviation: str) -> None:
    username = f"{abbreviation}_Editor"

    user = db.query(RaplaUser).filter(RaplaUser.username == username).first()
    if user is None:
        user = create_rapla_user(
            db,
            username=username,
            email=""
            password="",
            name=username,
            isadmin=False,
        )


    required_group_keys = [
        "read-events-from-others",
        "create-events",
        username,
    ]

    for group_key in required_group_keys:
        category = get_rapla_category_by_key(db, group_key)
        if category is None or category.id is None:
            continue

        add_rapla_group_for_user(db, rapla_user_id=cast(int, user.id), category_id=cast(int, category.id))


def seed_rapla_department_editor_users(db: Session) -> None:
    departments = db.query(Department).order_by(Department.abbreviation.asc()).all()
    for department in departments:
        abbreviation = cast(str | None, getattr(department, "abbreviation", None))
        if not abbreviation:
            continue

        _ensure_department_editor_user(db, abbreviation)


def seed_rapla_users(db: Session) -> tuple[int, str]:
    # Ensure Rapla admin exists (return its id/uuid for compatibility)
    admin = db.query(RaplaUser).filter(RaplaUser.username == "admin").first()
    if admin is None:
        admin = create_rapla_user(
            db,
            username="admin",
            email="",
            password="",
            name="",
            isadmin=True,
        )
        print("Created Rapla admin user.")
    else:
        print("Rapla admin user already exists.")

    # Ensure a "system" Rapla user exists. Use a unique non-empty email to avoid
    # colliding with the admin's empty email value.
    system = db.query(RaplaUser).filter(RaplaUser.username == "system").first()
    if system is None:
        try:
            system = create_rapla_user(
                db,
                username="system",
                email="system@system.local",
                password="",
                name="System",
                isadmin=True,
            )
            print("Created Rapla system user.")
        except Exception as e:
            print(f"Failed to create Rapla system user: {e}")
    else:
        print("Rapla system user already exists.")

    return cast(int, admin.id), cast(str, admin.uuid)
