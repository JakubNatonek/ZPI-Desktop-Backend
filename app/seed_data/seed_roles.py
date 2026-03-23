from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_user import Role


class RolaEnum(str, PyEnum):
    ADMIN = "admin"
    WYKLADOWCA = "wykladowca"
    CWICZENIA = "cwiczenia"
    LABORATORIUM = "laboratorium"
    SEMINARIUM = "seminarium"
    STUDENT = "student"
    INNE = "inne"


def seed_roles(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        for idx, role in enumerate(RolaEnum, start=1):
            existing_by_name = db.query(Role).filter_by(name=role.value).first()
            if existing_by_name:
                continue

            existing_by_id = db.query(Role).filter_by(id=idx).first()
            if existing_by_id is None:
                db.add(Role(id=idx, name=role.value))
            else:
                db.add(Role(name=role.value))

        if own_session:
            db.commit()
            print("Roles seeded.")
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_roles()
