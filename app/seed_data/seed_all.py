from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.seed_data.seed_admin import seed_admin
from app.seed_data.seed_departments import seed_departments
from app.seed_data.seed_roles import seed_roles
from app.seed_data.seed_room_type import seed_room_types
from app.seed_data.rapla.seed_rapla_all import seed_rapla_all
from app.seed_data.seed_users import seed_users


def seed_all() -> None:
    db: Session = SessionLocal()
    try:
        # for app
        seed_departments(db)
        seed_roles(db)
        seed_room_types(db)
        admin_id: int = seed_admin(db)
        seed_users(db)

        #for rapla
        seed_rapla_all(db, admin_id)

        print("All rapla seed data applied.")
    finally:
        db.close()
        print("Success.")


if __name__ == "__main__":
    seed_all()
