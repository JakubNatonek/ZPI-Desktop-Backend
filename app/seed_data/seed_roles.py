from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_role import create_role


class RolaEnum(str, PyEnum):
    ADMIN = "admin"
    WYKLADOWCA = "wykladowca"
    CWICZENIA = "cwiczenia"
    LABORATORIUM = "laboratorium"
    SEMINARIUM = "seminarium"
    STUDENT = "student"
    INNE = "inne"


def seed_roles(db: Session) -> None:
    for role in RolaEnum:
        try:
            create_role(db, role.value)
        except ValueError:
            # role already exists, ignore
            continue

    print("Roles seeded.")