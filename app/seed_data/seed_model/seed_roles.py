from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_department_role import create_role


class RolaEnum(str, PyEnum):
    ADMIN = "admin"
    WYKLADOWCA = "wykladowca"
    STUDENT = "student"
    RAPLA_EDITOR = "rapla_editor"
    INNE = "inne"


def seed_roles(db: Session) -> None:
    for role in RolaEnum:
        try:
            create_role(db, role.value)
        except ValueError:
            continue

    print("Roles seeded.")