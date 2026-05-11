from typing import cast

from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.models.model_department import Department
from app.models.model_role import Role
from app.seed_data.seed_model.seed_departments import DzialEnum
from app.seed_data.seed_model.seed_roles import RolaEnum
from app.cruds.crud_user import create_user
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_roles_for_user import add_role_to_user


def seed_admin(db: Session) -> int:
    # Getting Admin role
    admin_role = db.query(Role).filter(Role.name == RolaEnum.ADMIN.value).first()
    # lecturer_role = db.query(Role).filter(Role.name == RolaEnum.WYKLADOWCA.value).first()
    # Getting Admin department
    # enum values are (display_name, abbreviation); compare the display name (index 0)
    department = db.query(Department).filter(Department.name == DzialEnum.ADMIN.value[0]).first()

    if admin_role is None:
        raise RuntimeError("Missing admin role. Run seed_roles first.")

    # if lecturer_role is None:
    #     raise RuntimeError("Missing lecturer role. Run seed_roles first.")

    if department is None:
        raise RuntimeError("Missing admin department. Run seed_departments first.")

    created_user = create_user(
        db,
        first_name="admin",
        last_name="admin",
        login="admin",
        email="admin@admin.com",
        password_hash=hash_password("admin"),
        must_change_password=False,
    )

    # use CRUD helpers to create association rows
    add_department_to_user(db, cast(int, created_user.user_id), cast(int, department.id))
    add_role_to_user(db, cast(int, created_user.user_id), cast(int, admin_role.id))
    # add_role_to_user(db, cast(int, created_user.user_id), cast(int, lecturer_role.id))

    print("Admin user seeded.")
    return cast(int, created_user.user_id)