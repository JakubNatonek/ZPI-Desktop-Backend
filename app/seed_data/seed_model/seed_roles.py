from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.cruds.crud_role import create_role
from app.models.model_role import Role


class RolaEnum(str, PyEnum):
    ADMIN = "admin"
    WYKLADOWCA = "wykladowca"
    CWICZENIA = "cwiczenia"
    LABORATORIUM = "laboratorium"
    SEMINARIUM = "seminarium"
    STUDENT = "student"
    RAPLA_EDITOR = "rapla_editor"
    INNE = "inne"
def seed_roles(db: Session) -> None:
    for role in RolaEnum:
        try:
            create_role(db, role.value)
        except ValueError:
            continue

    lecturer_role_names = {"lecturer", "wykladowca", "cwiczenia", "laboratorium", "seminarium"}
    for role_name in lecturer_role_names:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role is not None:
            role.is_lecturer = True
            db.add(role)

    db.commit()
    print("Roles seeded.")