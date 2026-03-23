from enum import Enum as PyEnum

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.model_user import Department


class DzialEnum(str, PyEnum):
    ADMIN = "admin"
    INFORMATYKA = "informatyka"
    MECHATRONIKA = "mechatronika"
    ENERGETYKA = "energetyka"


def seed_departments(db: Session | None = None) -> None:
    own_session = db is None
    if db is None:
        db = SessionLocal()

    try:
        for idx, dep in enumerate(DzialEnum, start=1):
            existing_by_name = db.query(Department).filter_by(name=dep.value).first()
            if existing_by_name:
                continue

            existing_by_id = db.query(Department).filter_by(id=idx).first()
            if existing_by_id is None:
                db.add(Department(id=idx, name=dep.value))
            else:
                db.add(Department(name=dep.value))

        if own_session:
            db.commit()
            print("Departments seeded.")
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_departments()
