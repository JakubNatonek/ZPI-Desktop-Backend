from typing import cast

from sqlalchemy.orm import Session

from app.models.model_user import User
from app.models.model_department import Department
from app.models.model_role import Role
from app.seed_data.seed_departments import DzialEnum
from app.seed_data.seed_roles import RolaEnum
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_roles_for_user import add_role_to_user


def seed_admin(db: Session) -> int:
    admin = db.query(User).filter(User.email == "admin@admin.com").first()
    if admin:
        print("Admin user already exists.")
        return cast(int, admin.user_id)

    # Getting Admin role
    role = db.query(Role).filter(Role.name == RolaEnum.ADMIN.value).first()
    # Getting Admin department
    # enum values are (display_name, abbreviation); compare the display name (index 0)
    department = db.query(Department).filter(Department.name == DzialEnum.ADMIN.value[0]).first()

    if role is None or department is None:
        raise RuntimeError("Missing admin role/department. Run seed_roles_and_departments first.")

    created_user = User(
        first_name="admin",
        last_name="admin",
        login="admin",
        email="admin@admin.com",
        password_hash="$2b$12$zi7AdboGsbPpUp4j3qFpv.WTir3I5odeMnqzyUW4DTaN956Jq3.p.",
        plain_password=None,
        must_change_password=False,
    )

    db.add(created_user)
    db.flush()
    db.commit()
    db.refresh(created_user)

    # use CRUD helpers to create association rows
    add_department_to_user(db, cast(int, created_user.user_id), cast(int, department.id))
    add_role_to_user(db, cast(int, created_user.user_id), cast(int, role.id))

    print("Admin user seeded.")
    return cast(int, created_user.user_id)